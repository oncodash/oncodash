Oncodash frontend documentation
###############################

The interface of Oncodash is made with the `Vue.js (v3) <https://vuejs.org/>` framework and build with the `Vite <https://vitejs.dev/>` Bundler. It also uses `Typescript <https://www.typescriptlang.org/>` for better typing. The whole package is made on top of `node.js <https://nodejs.org/>`.
The source code can be found in the frontend folder at the root of the project:

- dist : The files of the build after running ``npm run build``.
- node_modules : The dependencies of the frontend, installed with ``npm install``.
- src : The actual source code with the Vue components.
- .editorconfig : The `EditorConfig <https://editorconfig.org/>` file code style.
- .node-version : The version of node.js used by this package.
- Dockerfile : The Dockerfile to build the frontend container.
- package-lock.json : The description of the manifest dependencies, written by node.js when dependencies changes. It must not be modified by hand, and must always be commited.
- package.json : The node.js package manifest, containing dependencing and metadata.
- tsconfig.json : The config file of typescript.
- vite.config.ts : The config file of Vite.

Source code
-----------

The main source code of the interface is under `frontend/src/`, oraganised as such :

- assets : contains the images and icons used by the components.
- components : the list of the Vue components that make the pages.
- models : the classes and custom types representing the interface entities, such as a patient or a sample.
- public : the list of files that `should not be processed by the bundler <https://vitejs.dev/guide/assets.html#the-public-directory>` and just served at the root of the website (e.g. robots.txt).
- api.ts : the list of API endpoints used by the components.
- apiState.ts : a `pinia store <https://pinia.vuejs.org/>` managing the state of the api requests.
- globals.css : the global CSS theme for the whole interface.
- index.html : the main html of the application.
- main.ts : the main entry point of the Vue components.
- router.ts : the list of pages and routing logic, handled by `vue-router <https://router.vuejs.org/>`.

Patient timelines
-----------------

The patient timelines are rendered using `canvajs <https://canvasjs.com/>`, specifically `@canvasjs/vue-stockcharts` as declared in the package.json.

Vue components
--------------

The Oncodash interface uses the `Vue framework <https://vuejs.org/>` the implement the graphical components.
It builds on top of standard HTML, CSS, and JavaScript and provides a declarative, component-based programming model that helps you efficiently develop user interfaces of any complexity. The components themselves are written as `Single-File Components <https://vuejs.org/guide/introduction.html#single-file-components>` (SFC) ending with the `.vue` extension.
