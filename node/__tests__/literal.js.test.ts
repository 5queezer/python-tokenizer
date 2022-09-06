import {Parser, Program} from '../src/Parser'
import * as assert from "assert";

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
    assert.deepEqual(ast, expected)
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
    assert.deepEqual(ast, expected)
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
    assert.deepEqual(ast, expected)
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
    assert.deepEqual(ast, expected)
})
