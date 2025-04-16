<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class Template extends Migration
{
    public function up()
    {
        $this->forge->addField([
            'id'=>[
                'type' => 'INT',
                'auto_increment'=>true,
                'unsigned'=> true
                ],
            'username'=>[
                'type' => 'VARCHAR',
                'constraint' => 30,
                'unique' => true,
                'null' => true
                ],
                
            'password'=>[
                'type' => 'VARCHAR',
                'constraint' => 255,
                'null' => true
                ],
            'email'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'unique' => true,
                'null' => true
                ],
            'authority'=>[
                'type' => 'INT',
                'unsigned'=> true,
                'null' => true
            ]
            ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('users');

        $this->forge->addField([
            'id'=>[
                'type' => 'INT',
                'auto_increment'=>true,
                'unsigned'=> true
                ],
            'road_name'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],
            'date'=>[
                'type' => 'DATE',
                'null' => true
                ],
            ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('roads');

        $this->forge->addField([
            'id'=>[
                'type' => 'INT',
                'auto_increment'=>true,
                'unsigned'=> true
                ],
            'videoname'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],
            'road'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],
            'is_run'=>[
                'type'=>'BOOLEAN',
                'null' => true
            ],
            'date'=>[
                'type' => 'DATE',
                'null' => true
                ],
            'video_path'=>[
                'type' => 'VARCHAR',
                'constraint' => 100,
                'null' => true
                ],
            ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('videos');

        $this->forge->addField([
            'id'=>[
                'type' => 'INT',
                'auto_increment'=>true,
                'unsigned'=> true
                ],
            'videoname'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],
            'road'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],
            'is_run'=>[
                'type'=>'BOOLEAN',
                'null' => true
            ],
            'date'=>[
                'type' => 'DATE',
                'null' => true
                ],
            'video_path'=>[
                'type' => 'VARCHAR',
                'constraint' => 100,
                'null' => true
                ],
            ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('autovideos');

        $this->forge->addField([
            'id'=>[
                'type' => 'INT',
                'auto_increment'=>true,
                'unsigned'=> true
                ],

            'license_plate'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],

            'date'=>[
                'type' => 'DATE',
                'constraint' => 50,
                'null' => true
            ],

            'road'=>[
                'type' => 'VARCHAR',
                'constraint' => 50,
                'null' => true
                ],

            'video_path'=>[
                'type'=>'VARCHAR',
                'null' => true
            ],

            'img_path'=>[
                'type' => 'VARCHAR',
                'null' => true
                ]
            ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('violatingCars');




        $this->db->query("INSERT INTO violatingCars (license_plate, date, road, video_path, img_path) VALUES ('1234(測試資料)', '2023-04-11', 'A','videos/20230301_125551_0192_A.mp4','');");
        $this->db->query("INSERT INTO roads ('road_name', 'date') VALUES ('A', '2023-04-11');");
        #管理者，不需要註冊帳號
        $this->db->query("INSERT INTO users (username, email, password, authority) VALUES ('a', 'a@gmail.com', 'a',1);");
    }

    public function down()
    {
        $this->forge->dropTable('users');
        $this->forge->dropTable('roads');
        $this->forge->dropTable('videos');
        $this->forge->dropTable('autovideos');
        $this->forge->dropTable('violatingCars');
    }
}
