import * as Utils from '../utils';

export function calculateCircumference(diameter: number): number {
    return diameter * Utils.PI;
}

export function displayGreeting(name: string): void {
    console.log(Utils.greet(name));
}