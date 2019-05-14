module.exports = {
    root: true,
    parserOptions: {
        ecmaVersion: 2017,
        sourceType: 'module'
    },
    env: {
        browser: true,
    },
    rules: {
        "no-debugger": process.env.NODE_ENV === "production" ? 2 : 0,
        "arrow-parens": 0,
        "no-empty": "error",
        "no-extra-semi": "error",
        "semi": ["error", "never"],
        "generator-star-spacing": 0,
        "no-unused-vars": 0,
        "indent": ["error", 4, {
            "SwitchCase": 1
        }],
        "space-before-function-paren": ["error", {
            "anonymous": "always", 
            "named": "always",
            "asyncArrow": "always" 
        }],
        "no-trailing-spaces": ["error", {
            "skipBlankLines": true 
        }],
        "comma-dangle": ["error", "never"],
        "key-spacing": ["error", {
            "beforeColon": false 
        }],
        "keyword-spacing": ["error", {
            "before": true, 
            "after": true
        }],
        "space-infix-ops": "error",
        "spaced-comment": ["error", "always"],
    },
    extends: [
        "plugin:vue/essential"
    ]
}