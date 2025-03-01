import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


device = torch.device("cuda:0")


bn_momentum = 0.1

class Encoder(nn.Module):
    def __init__(self, input_channels):
        super(Encoder, self).__init__()

        self.enco1 = nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64, momentum=bn_momentum),
            nn.ReLU()
        )
        self.enco2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128, momentum=bn_momentum),
            nn.ReLU()
        )
        self.enco3 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256, momentum=bn_momentum),
            nn.ReLU()
        )
        self.enco4 = nn.Sequential(
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512, momentum=bn_momentum),
            nn.ReLU()
        )
        self.enco5 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512, momentum=bn_momentum),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512, momentum=bn_momentum),
            nn.ReLU()
        )

    def forward(self, x):
        id = []

        x = self.enco1(x)
        x, id1 = F.max_pool2d(x, kernel_size=2, stride=2, return_indices=True)  # 保留最大值的位置
        id.append(id1)
        x = self.enco2(x)
        x, id2 = F.max_pool2d(x, kernel_size=2, stride=2, return_indices=True)
        id.append(id2)
        x = self.enco3(x)
        x, id3 = F.max_pool2d(x, kernel_size=2, stride=2, return_indices=True)
        id.append(id3)
        x = self.enco4(x)
        x, id4 = F.max_pool2d(x, kernel_size=2, stride=2, return_indices=True)
        id.append(id4)
        x = self.enco5(x)
        x, id5 = F.max_pool2d(x, kernel_size=2, stride=2, return_indices=True)
        id.append(id5)
        return x

class Feature_extractor(nn.Module):
    def __init__(self, latent_dim):
        super(Feature_extractor, self).__init__()
        self.encoder = Encoder(3)
        self.final = nn.Sequential(
            nn.Linear(512*7*7, latent_dim),
            nn.BatchNorm1d(latent_dim, momentum=0.01))

    def forward(self, x):
        with torch.no_grad():
            x = self.encoder(x)
        x= x.view(x.size(0), -1)
        return self.final(x)


class LSTM(nn.Module):
    def __init__(self, latent_dim, num_layers, hidden_dim, bidirectional):
        super(LSTM, self).__init__()
        self.lstm = nn.LSTM(
            latent_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            bidirectional=bidirectional,
        )
        self.hidden_state = None

    def reset_hidden_state(self):
        self.hidden_state = None

    def forward(self, x):
        x, self.hidden_state = self.lstm(x, self.hidden_state)
        return x


class Attention(nn.Module):
    def __init__(self, latent_dim, hidden_dim, attention_dim):
        super(Attention, self).__init__()
        self.latent_attention = nn.Linear(latent_dim, attention_dim)
        self.hidden_attention = nn.Linear(hidden_dim, attention_dim)
        self.joint_attention = nn.Linear(attention_dim, 1)

    def forward(self, latent_repr, hidden_repr):
        if hidden_repr is None:
            hidden_repr = [
                Variable(
                    torch.zeros(
                        latent_repr.size(0), 1, self.hidden_attention.in_features
                    ),
                    requires_grad=False,
                ).float()
            ]
        h_t = hidden_repr[0]
        latent_att = self.latent_attention(latent_att)
        hidden_att = self.hidden_attention(h_t)
        joint_att = self.joint_attention(F.relu(latent_att + hidden_att)).squeeze(-1)
        attention_w = F.softmax(joint_att, dim=-1)
        return attention_w


class CNNLSTM(nn.Module):
    def __init__(
        self,
        num_classes,
        latent_dim=512,
        lstm_layers=1,
        hidden_dim=1024,
        bidirectional=True,
        attention=True,
    ):
        super(CNNLSTM, self).__init__()
        self.weights_new = self.state_dict()
        self.feature_extractor = Feature_extractor(latent_dim)
        self.lstm = LSTM(latent_dim, lstm_layers, hidden_dim, bidirectional)
        self.output_layers = nn.Sequential(
            nn.Linear(2 * hidden_dim if bidirectional else hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes),
            nn.Softmax(dim=-1),
        )
        self.attention = attention
        self.attention_layer = nn.Linear(
            2 * hidden_dim if bidirectional else hidden_dim, 1
        )

    def forward(self, x, true_length):
        batch_size, seq_length, c, h, w = x.shape

        with torch.no_grad():
            mask = torch.zeros((batch_size, seq_length))
            true_lengths_tensor = torch.tensor(true_length)
            indices = torch.arange(seq_length).expand(batch_size, seq_length)
            tmp = indices < true_lengths_tensor.unsqueeze(1)
            mask[tmp] = 1
        mask = mask.to(device)
        true_lengths_tensor = true_lengths_tensor.to(device)

        x = x.view(batch_size * seq_length, c, h, w)
        x = self.feature_extractor(x)
        x = x.view(batch_size, seq_length, -1)

        #通過LSTM前先壓縮在解壓縮
        x = pack_padded_sequence(x, true_length, batch_first=True, enforce_sorted=False)
        x = self.lstm(x)
        x, _ = pad_packed_sequence(x, batch_first=True)
        # print(x.shape)
     
        if self.attention:
            attention_scores = self.attention_layer(x).squeeze(-1)
            attention_scores = attention_scores.masked_fill(mask == 0, -1e9)
            attention_w = F.softmax(attention_scores, dim=-1)
            x = torch.sum(attention_w.unsqueeze(-1) * x * mask.unsqueeze(-1) , dim = 1)
        else:
            print(x.shape)
            print(true_lengths_tensor.shape)
            x = x.gather(dim = 1,index = true_lengths_tensor.unsqueeze(-1) )
            x = x[:, -1]
            print(x.shape)
        return self.output_layers(x)


    def load_weights(self, weights_path):
        weights = torch.load(weights_path)
        del weights["deco1.0.weight"]
        del weights["deco1.0.bias"]
        del weights["deco1.1.weight"]
        del weights["deco1.1.bias"]
        del weights["deco1.1.running_mean"]
        del weights["deco1.1.running_var"]
        del weights["deco1.1.num_batches_tracked"]
        del weights["deco1.3.weight"]
        del weights["deco1.3.bias"]
        del weights["deco1.4.weight"]
        del weights["deco1.4.bias"]
        del weights["deco1.4.running_mean"]
        del weights["deco1.4.running_var"]
        del weights["deco1.4.num_batches_tracked"]        
        del weights["deco1.6.weight"]
        del weights["deco1.6.bias"]
        del weights["deco1.7.weight"]
        del weights["deco1.7.bias"]
        del weights["deco1.7.running_mean"]
        del weights["deco1.7.running_var"]
        del weights["deco1.7.num_batches_tracked"]
        del weights["deco2.0.weight"]
        del weights["deco2.0.bias"]
        del weights["deco2.1.running_mean"]
        del weights["deco2.1.running_var"]
        del weights["deco2.1.num_batches_tracked"]
        del weights["deco2.3.weight"]
        del weights["deco2.3.bias"]
        del weights["deco2.4.weight"]
        del weights["deco2.4.bias"]
        del weights["deco2.4.running_mean"]
        del weights["deco2.4.running_var"]
        del weights["deco2.4.num_batches_tracked"]        
        del weights["deco2.6.weight"]
        del weights["deco2.6.bias"]
        del weights["deco2.7.weight"]
        del weights["deco2.7.bias"]
        del weights["deco2.7.running_mean"]
        del weights["deco2.7.running_var"]
        del weights["deco2.7.num_batches_tracked"]
        del weights["deco3.0.weight"]
        del weights["deco3.0.bias"]
        del weights["deco3.1.running_mean"]
        del weights["deco3.1.running_var"]
        del weights["deco3.1.num_batches_tracked"]
        del weights["deco3.3.weight"]
        del weights["deco3.3.bias"]
        del weights["deco3.4.weight"]
        del weights["deco3.4.bias"]
        del weights["deco3.4.running_mean"]
        del weights["deco3.4.running_var"]
        del weights["deco3.4.num_batches_tracked"]        
        del weights["deco3.6.weight"]
        del weights["deco3.6.bias"]
        del weights["deco3.7.weight"]
        del weights["deco3.7.bias"]
        del weights["deco3.7.running_mean"]
        del weights["deco3.7.running_var"]
        del weights["deco3.7.num_batches_tracked"] 
        del weights["deco4.1.running_mean"]
        del weights["deco4.0.weight"]
        del weights["deco4.0.bias"]
        del weights["deco4.1.running_var"]
        del weights["deco4.1.num_batches_tracked"]
        del weights["deco4.3.weight"]
        del weights["deco4.3.bias"]
        del weights["deco4.4.weight"]
        del weights["deco4.4.bias"]
        del weights["deco4.4.running_mean"]
        del weights["deco4.4.running_var"]
        del weights["deco4.4.num_batches_tracked"]        
        del weights["deco5.0.weight"]
        del weights["deco5.0.bias"]
        del weights["deco5.1.running_var"]
        del weights["deco5.1.num_batches_tracked"]
        del weights["deco5.3.weight"]
        del weights["deco5.3.bias"]

        names = []
        for key, value in self.feature_extractor.encoder.state_dict().items():

            names.append(key)

        for name, dict in zip(names, weights.items()):
            self.weights_new[name] = dict[1]

        self.feature_extractor.encoder.load_state_dict(self.weights_new)


