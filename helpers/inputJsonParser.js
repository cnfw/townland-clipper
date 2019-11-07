'use strict';

const fileHandler = require("./fileHandler");
const constants = require("./constants");

module.exports = {
    jsonToObject: (path) => {
        let rawData = fileHandler.readFile(path);

        return JSON.parse(rawData);
    },

    getListOfTownlandsInCounty: (fullDataset, county) => {
        county = county.toUpperCase();
        return fullDataset.features.filter(townlandObject => {
            let properties = townlandObject.properties;

            return properties.COUNTY === county;
        })
    },

    cleanTownlandObjects: (inputTownlands) => {
        inputTownlands.forEach(townland => {
            let townlandProperties = townland.properties;

            Object.keys(townlandProperties).forEach((property) => {
                constants.townlandObjectPropertiesToKeep.includes(property) || delete townlandProperties[property];
            });
        });
    },

    renameTdEnglishToName: (inputTownlands) => {
        inputTownlands.forEach(townland => {
            let townlandProperties = townland.properties;

            Object.defineProperty(townlandProperties, constants.keyNameForGeometriesScript,
                Object.getOwnPropertyDescriptor(townlandProperties, constants.keyToChangeToName));

            delete townlandProperties[constants.keyToChangeToName];
        });
    },

    reduceTownlandListGeometry: (inputTownlands) => {
        inputTownlands.forEach(townland => {
            let traverseAndRoundArray = (input) => {
                if (Array.isArray(input[0])) {
                    // If the first item in the array is another array, 
                    // then we need to go down another level. This is done 
                    // by recursion since we don't know how many levels 
                    // down the original datasets can go.
                    for (let i = 0; i < input.length; i++) {
                        input[i] = traverseAndRoundArray(input[i]);
                    }
                } else {
                    for (let i = 0; i < input.length; i++) {
                        // Rounds to 4dp
                        input[i] = Math.round(input[i] * 1e4) / 1e4;
                    }
                }

                return input;
            }

            townland.geometry.coordinates = traverseAndRoundArray(townland.geometry.coordinates);
        });
    }
}
