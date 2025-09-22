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
// $routes->get('MonitorController', 'MonitorController::index', ['filter' => ['auth']]);
$routes->get('ViolationController', 'ViolationController::index');
$routes->get('get_violation_images', 'ViolationController::get_violation_images');
$routes->post('get_violation_car_data', 'MonitorController::get_violation_car_data');
$routes->get('history', 'LiveFeedController::violation_history', ['filter' => ['auth']]);
$routes->group('LiveFeedController', ['filter' => ['auth']], function($routes) {
    $routes->get('/', 'LiveFeedController::index');
    $routes->get('api', 'LiveFeedController::api');
    $routes->post('start_detection', 'LiveFeedController::start_detection');
    $routes->post('stop', 'LiveFeedController::stop');
    $routes->get('get_history', 'LiveFeedController::get_history');
    $routes->get('violation_history', 'LiveFeedController::violation_history');
});
