
import {Tokenizer, Token} from "./Tokenizer";

export type Program = {
    type: string,
    body: Token
}

export class Parser {
    private _string: string;
    private _tokenizer: Tokenizer;
    private _lookahead: Token;

    constructor() {
        this._string = '';
        this._tokenizer = new Tokenizer();
    }

    /**
     * Parses a string into an AST
     * @param string
     */
    parse(string: string): Program {
        this._string = string
        this._tokenizer.init(string)

        // Prime the tokenizer to obtain the first token
        this._lookahead = this._tokenizer.getNextToken()

        return this.Program()
    }

    Program(): Program {
        return {
            type: 'Program',
            body: this.Literal()
        }
    }

    Literal(): Token {
        switch (this._lookahead.type) {
            case 'NUMBER': return this.NumericLiteral()
            case 'STRING': return this.StringLiteral()
        }
        throw new SyntaxError(`Literal: Unexpected literal production`)
    }

    private _eat(tokenType: string): Token {
        const token = this._lookahead
        if (token == null) {
            throw new SyntaxError(`Unexpected end of input, expected "${tokenType}"`)
        }
        if (token.type !== tokenType) {
            throw new SyntaxError(`Unexpected token: "${token.value}, expected: "${tokenType}"`)
        }

        // Advance to next token
        this._lookahead = this._tokenizer.getNextToken()
        return token
    }

    private NumericLiteral(): Token {
        const token = this._eat('NUMBER')
        return {
            type: 'NumericLiteral',
            value: Number(token.value)
        }
    }

    private StringLiteral(): Token {
        const token = this._eat('STRING')
        return {
            type: 'StringLiteral',
            value: String(token.value).slice(1,-1)
        }
    }
}

