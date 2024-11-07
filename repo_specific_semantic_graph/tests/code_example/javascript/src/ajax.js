export function ajaxLoader($parse, prepareWindowEvents) {
    return {
        restrict: 'AE',
        scope: false,
        template: require('./ajax-loader.jade'),
    }
}