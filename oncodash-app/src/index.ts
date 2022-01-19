/* Fake file to make sphinx-js work (to be removed soon) */
interface Person {
  age: number;
  name: string;
  say(): string;
}

const mike = {
  age: 25,
  name: 'Mike',
  say() {
    return `My name is ${this.name} and I'm ${this.age} years old!`;
  },
};

/**
 * This function says who I am and my age!
 *
 * @param {Person} person - TODO
 * @returns {Said} TODO.
 */

function sayIt(person: Person) {
  return person.say();
}

console.log(sayIt(mike));
