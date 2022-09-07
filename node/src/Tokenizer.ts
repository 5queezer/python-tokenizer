export type Token = {
    type: string,
    value: string | number
}


const Spec: [RegExp, Token["type"] | null][] = [
    // Whitespace
    [/^\s+/, null],

    // Comments
    // Skip single line-comments
    [/^\/\/.*/, null],

    // Skip multi line-comments
    [/^\/\*[\s\S]*?\*\//, null],

    // Strings
    [/^'[^']*'/, 'STRING'],
    [/^"[^"]*"/, 'STRING'],

    // Numbers
    [/^\d+/, 'NUMBER']
]

export class Tokenizer {
    private _string: string;
    private _cursor: number;

    constructor() {
    }

    public init(string: string) {
        this._string = string
        this._cursor = 0
    }

    public getNextToken(): Token {
        if (!this._hasMoreTokens()) {
            return null;
        }
        const string = this._string.slice(this._cursor)
        for (const [regexp, tokenType] of Spec) {
            const tokenValue = this._match(regexp, string)
            if (tokenValue === null) {
                continue
            }
            if (tokenType === null) {
                return this.getNextToken()
            }
            return {
                type: tokenType,
                value: tokenValue
            }
        }
        throw new SyntaxError(`Unexpected token: "${this._string[0]}"`)
    }

    private _hasMoreTokens(): boolean {
        return this._cursor < this._string.length;
    }

    public isEOF(): boolean {
        return this._cursor === this._string.length
    }

    private _match(regexp: RegExp, string: string): Token["value"] | null {
        const matched = regexp.exec(string)
        if (matched === null) {
            return null
        }
        this._cursor += matched[0].length
        return matched[0]
    }
}
