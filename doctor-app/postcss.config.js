module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
    {
      postcssPlugin: 'remove-charset',
      AtRule: {
        charset(atRule) {
          if (atRule.name === 'charset') {
            atRule.remove();
          }
        },
      },
    },
  ],
}

