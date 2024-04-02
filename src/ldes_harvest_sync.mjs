import { newEngine } from "@treecg/actor-init-ldes-client";
import fs from "fs";
import { fileURLToPath } from "url";
import path from "path";
import YAML from "yaml";

// load in the ..//config.yml file to get the configuration
// load in the ../config.yml file to get the configuration

const config = fs.readFileSync("../config.yml", "utf8");
console.log(config);
//extract the values from the config file into a dictionary
const configValues = YAML.parse(config);
console.log(configValues);

//constants
const __dirname = path.dirname(fileURLToPath(import.meta.url));
let OUTPUT_FOLDER = path.join(__dirname, "../");
console.log(OUTPUT_FOLDER);

// for sources in configValues["sources"]:
for (let source in configValues["sources"]) {
  console.log(source);
  console.log(configValues["sources"][source]);
  let url = configValues["sources"][source]["url"];
  let language = configValues["sources"][source]["language"];
  let name_folder = configValues["sources"][source]["name"];
  let items = configValues["sources"][source]["items"];
  console.log(url);

  //check if a folder is present in OUTPUT_FOLDER that is named after name_folder
  //if not create the folder
  let folder = path.join(OUTPUT_FOLDER, name_folder);
  console.log(folder);
  try {
    if (!fs.existsSync(folder)) {
      console.log("folder does not exist");
      fs.mkdirSync(folder);
    }
  } catch (e) {
    console.error(e);
  }

  //!This pulls the first url of the ldes stream but then does not continue to the next one

  try {
    let options = {
      representation: "Object", //Object or Quads
      requestHeaders: {
        // Optional request headers, useful when e.g. the endpoint requires Auth headers
        Accept: "text/turtle",
      },
      emitMemberOnce: true,
      disablePolling: true,
      requestsPerMinute: 40,
    };
    let LDESClient = new newEngine();
    let eventstreamSync = LDESClient.createReadStream(url, options);
    // OR if you have a previous state
    // let eventstreamSync = LDESClient.createReadStream(url, options, state);
    eventstreamSync.on("data", (member) => {
      if (options.representation) {
        if (options.representation === "Object") {
          const memberURI = member.id;
          console.log(memberURI);
          const object = member.object;
          console.log(object);
        }
      } else {
        console.log(member);
      }

      // Want to pause event stream?
      eventstreamSync.pause();
    });
    eventstreamSync.on("metadata", (metadata) => {
      if (metadata.treeMetadata) console.log(metadata.treeMetadata); // follows the structure of the TREE metadata extractor (https://github.com/TREEcg/tree-metadata-extraction#extracted-metadata)
      console.log(metadata.url); // page from where metadata has been extracted
    });
    eventstreamSync.on("pause", () => {
      // Export current state, but only when paused!
      let state = eventstreamSync.exportState();
    });
    eventstreamSync.on("end", () => {
      console.log("No more data!");
    });
  } catch (e) {
    console.error(e);
  }
}
