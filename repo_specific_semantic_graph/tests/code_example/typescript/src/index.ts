import { greet, PI } from './utils';
import { add } from './utils/another';
import { calculateCircumference, displayGreeting } from './services/service';

// Absolute import
// @ts-ignore
import * as path from 'path';

const userName = 'John';
displayGreeting(userName);

console.log(`The value of PI is ${PI}`);
console.log(`10 + 20 = ${add(10, 20)}`);
console.log(`Circumference for diameter of 2: ${calculateCircumference(2)}`);

// @ts-ignore
console.log('The current filename is:', path.basename(__filename));