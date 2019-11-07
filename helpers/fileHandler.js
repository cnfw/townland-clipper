const fs = require('fs')

module.exports = {
    checkFileExists: (path) => {
        try {
            return fs.existsSync(path);
        } catch (err) {
            return false;
        }
    },

    readFile: (path) => {
        try {
            return fs.readFileSync(path);
        } catch (err) {
            return false;
        }
    },

    writeOutputfile: (path, data) => {
        try {
            fs.writeFileSync(path, data);

            return true;
        } catch (err) {
            return false;
        }
    }
}