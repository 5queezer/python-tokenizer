import {Parser, Program} from '../src/Parser'
import {expect, test} from '@jest/globals';

test('NumericLiteral', () => {
    const program = '42';
    const parser = new Parser();
    const ast = parser.parse(program)
    const expected: Program = {
        type: 'Program',
        body: {
            type: 'NumericLiteral',
            value: 42,
        },
    }
    expect(ast).toStrictEqual(expected)
})

test('StringLiteral', () => {
    const program = '"hello"';
    const parser = new Parser();
    const ast = parser.parse(program)
    const expected: Program = {
        type: 'Program',
        body: {
            type: 'StringLiteral',
            value: 'hello',
        },
    }
    expect(ast).toStrictEqual(expected)
})

test('Single Line Comment', () => {
    const program = `
    // Number: 42
    42
    `;
    const parser = new Parser();
    const ast = parser.parse(program)
    const expected: Program = {
        type: 'Program',
        body: {
            type: 'NumericLiteral',
            value: 42,
        },
    }
    expect(ast).toStrictEqual(expected)
})

test('Multi Line Comment', () => {
    const program = `
        /**
         * Documentation comment:
         */
         
        "hello" 
    `;
    const parser = new Parser();
    const ast = parser.parse(program)
    const expected: Program = {
        type: 'Program',
        body: {
            type: 'StringLiteral',
            value: 'hello',
        },
    }
    expect(ast).toStrictEqual(expected)
})
