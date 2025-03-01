<?php

use CodeIgniter\Router\RouteCollection;
$routes->setDefaultNamespace('App\Controllers');
$routes->setDefaultController('Home');
$routes->setDefaultMethod('index');
$routes->setTranslateURIDashes(false);
$routes->set404Override();
$routes->setAutoRoute(true);
// The Auto Routing (Legacy) is very dangerous. It is easy to create vulnerable apps
// where controller filters or CSRF protection are bypassed.
// If you don't want to define all routes, please use the Auto Routing (Improved).
// Set `$autoRoutesImproved` to true in `app/Config/Feature.php` and set the following to true.


/**
 * @var RouteCollection $routes
 */
$routes->get('/Home', 'Home::index', ['filter' => ['auth']]);
$routes->get('/', 'LoginController::index', ['filter' => ['auth_home']]);
$routes->get('UploadController', 'UploadController::index', ['filter' => ['auth']]);
$routes->get('RunController', 'RunController::index', ['filter' => ['auth']]);
$routes->get('FindController', 'FindController::index', ['filter' => ['auth']]);
$routes->get('MonitorController', 'MonitorController::index', ['filter' => ['auth']]);
// $routes->get('LiveFeedController/four_panel_monitor', 'LiveFeedController::four_panel_monitor');
$routes->get('LiveFeedController', 'LiveFeedController::index');




$routes->post('get_violation_car_data', 'MonitorController::get_violation_car_data');
