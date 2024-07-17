// Main entry point
import { funcA } from './utils/utilA';
import * as utilB from './utils/utilB';
import Component from './components/Component';

console.log(funcA());
console.log(utilB.funcB());
console.log(new Component().render());
