
import {Tokenizer, TokenType} from "./Tokenizer";

export type Program = {
    type: string,
    body: TokenType
}

export class Parser {
    private _string: string;
    private _tokenizer: Tokenizer;
    private _lookahead: TokenType;

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

    Literal(): TokenType {
        switch (this._lookahead.type) {
            case 'NUMBER': return this.NumericLiteral()
            case 'STRING': return this.StringLiteral()
        }
        throw new SyntaxError(`Literal: Unexpected literal production`)
    }

    private _eat(tokenType: string): TokenType {
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

    private NumericLiteral(): TokenType {
        const token = this._eat('NUMBER')
        return {
            type: 'NumericLiteral',
            value: Number(token.value)
        }
    }

    private StringLiteral(): TokenType {
        const token = this._eat('STRING')
        return {
            type: 'StringLiteral',
            value: String(token.value).slice(1,-1)
        }
    }
}

