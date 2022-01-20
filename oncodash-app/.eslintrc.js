module.exports = {
    env: {
        browser: true,
        es6: true,
    },
    parser: "@typescript-eslint/parser",
    plugins: ["@typescript-eslint"],
    extends: [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "prettier",
    ],
    parserOptions: {
        sourceType: "module",
    },
    rules: {
        "no-new-func": "off",
        "no-bitwise": "off",
        "no-undefined": "off",
        "no-nested-ternary": "off",
        "dot-notation": "off",
        "no-unused-vars": ["error", { args: "none" }],
        "require-await": "off",
    },
};
