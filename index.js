#!/usr/bin/env node

const argv = require('yargs').argv;
const constants = require("./helpers/constants");
const fileHandler = require("./helpers/fileHandler");
const inputJsonParser = require("./helpers/inputJsonParser");

////////////////
// Get inputs //
////////////////

// Input JSON
const inputJsonFilePath = argv.input;

if (inputJsonFilePath === undefined) {
    console.log("No input file specified. Please specify an input file with --input=path");
    return;
} else if (!fileHandler.checkFileExists(inputJsonFilePath)) {
    console.log("Input file does not exist or cannot be read by node. Please check that the path exists and try again.");
    return;
}
// Output directory
const outputDirectory = argv.output;

if (outputDirectory === undefined) {
    console.log("No output directory specified. Please specify an output directory with --output=path/to/directory/");
    return;
} else if (!fileHandler.checkFileExists(outputDirectory)) {
    console.log("Output directory does not exist or cannot be seen by node. Please check that the path exists and try again.");
    return;
}

// Reduce flag
const reduce = argv.reduce;

// Dry run
const dryRun = argv.dryRun;

////////////////
// Parse JSON //
////////////////
let townlandsData = inputJsonParser.jsonToObject(inputJsonFilePath);

for (let county of constants.counties) {
    console.log("Extracting townlands for " + county);

    let countyTownlands = {
        type: "FeatureCollection",
        features: []
    }

    let filteredTownlands = inputJsonParser.getListOfTownlandsInCounty(townlandsData, county);

    inputJsonParser.cleanTownlandObjects(filteredTownlands);
    inputJsonParser.renameTdEnglishToName(filteredTownlands);

    if (reduce) {
        inputJsonParser.reduceTownlandListGeometry(filteredTownlands);
    }

    countyTownlands.features = filteredTownlands;

    let reducedString = (reduce) ? "reduced_" : "";

    let outputPath = outputDirectory + "/townlands_" + reducedString + county + ".geojson";
    let outputFileContents = JSON.stringify(countyTownlands);

    if (!dryRun) {
        fileHandler.writeOutputfile(outputPath, outputFileContents);
    }
}

console.log("Completed.");
