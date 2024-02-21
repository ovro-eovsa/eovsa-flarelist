# EOVSA Flarelist Website

The EOVSA Flarelist Website provides a dynamic interface for querying and displaying solar flare data collected by the Expanded Owens Valley Solar Array ([EOVSA](http://ovsa.njit.edu)). It features a user-friendly web interface for accessing flare lists, detailed temporal/spectral data, and related quicklook imaging data products.

## Accessing the Website

The website can be accessed through the following URL: [http://ovsa.njit.edu/flarelist](http://ovsa.njit.edu/flarelist).

## File Structure Overview

- **`routes.py`**: Main routing file defining URL routes for the application.
- **`wsgi.py`**: Entry point for running the Flask application.
- **`blueprints/`**: Contains modular Flask blueprints.
  - **`examples.py`**: Blueprint for querying the database and handling specific page routes.
- **`templates/`**: Directory for Jinja2 HTML templates.
- **`core/`**: Contains core functionality and utilities.
  - **`eovsa_bundle.py`**: Manages bundling of CSS and JS files.
- **`static/`**: Static files for the website.
  - **`js/`**: Custom JavaScript files.
  - **`css/`**: Custom CSS stylesheets.
  - **`vendor/`**: Third-party libraries and frameworks.
    - **`css/`**: Third-party CSS files.
    - **`js/`**: Third-party JavaScript files.
  - **`images/`**: Static images used in the website.

## Inspiration

This website is inspired by the [STIX Data Center](https://datacenter.stix.i4ds.net/view/ql/lightcurves). The source code for the inspiration project can be found at [STIX Data Center GitHub Repository](https://github.com/drhlxiao/minisdc).

## Contributing

We welcome contributions to the EOVSA Flarelist Website project. If you're interested in contributing, please fork the repository and submit your pull requests for review.

## License
Apache License 2.0
