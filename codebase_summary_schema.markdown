# Codebase Summary Schema

Below is the JSON schema for the codebase summary presented in a table format, detailing each section's properties, their types, descriptions, and whether they are required. The schema adheres to JSON Schema Draft 2020-12 standards.

| **Section**                     | **Property**                     | **Type**                     | **Description**                                                                 | **Required** |
|--------------------------------|-----------------------------------|------------------------------|---------------------------------------------------------------------------------|--------------|
| **Root**                       | id                               | string                       | Unique identifier for the codebase summary                                      | Yes          |
| **project_metadata**           |                                  | object                       | Metadata about the project                                                      | Yes          |
|                                | project_name                     | string                       | Name of the project                                                             | Yes          |
|                                | version                          | string                       | Version of the project                                                          | Yes          |
|                                | description                      | string                       | Description of the project                                                      | Yes          |
|                                | main_language                    | string                       | Primary programming language used                                               | Yes          |
|                                | license                          | string                       | License under which the project is distributed                                  | Yes          |
|                                | authors                          | array[string]                | List of authors contributing to the project                                     | Yes          |
|                                | dependencies                     | array[object]                | List of project dependencies                                                    | Yes          |
|                                | dependencies.name                | string                       | Name of the dependency                                                          | Yes          |
|                                | dependencies.version             | string                       | Version of the dependency                                                       | Yes          |
|                                | last_updated                     | string (date-time)           | Date and time of last update (ISO 8601 format)                                  | Yes          |
| **file_details**               |                                  | array[object]                | Array of file objects in the codebase                                           | Yes          |
|                                | path                             | string                       | File path relative to the project root                                          | Yes          |
|                                | file_size_bytes                  | integer                      | Size of the file in bytes                                                       | Yes          |
|                                | language                         | string                       | Programming language of the file                                                | Yes          |
|                                | lines_of_code                    | integer                      | Number of lines of code in the file                                             | Yes          |
|                                | checksum                         | string                       | SHA-256 checksum of the file (64 hexadecimal characters)                        | Yes          |
| **code_metrics**               |                                  | object                       | Metrics summarizing the codebase                                                | Yes          |
|                                | total_lines_of_code              | integer                      | Total lines of code across all files                                            | Yes          |
|                                | comment_lines                    | integer                      | Total number of comment lines                                                   | Yes          |
|                                | blank_lines                      | integer                      | Total number of blank lines                                                     | Yes          |
|                                | test_coverage_percent            | number                       | Percentage of code covered by tests (0-100)                                     | Yes          |
|                                | code_duplication_percent         | number                       | Percentage of duplicated code (0-100)                                           | Yes          |
|                                | cyclomatic_complexity_average    | number                       | Average cyclomatic complexity across the codebase                               | Yes          |
| **security_vulnerabilities**    |                                  | array[object]                | Array of security vulnerability objects                                         | Yes          |
|                                | vulnerability_id                 | string                       | Unique identifier for the vulnerability                                         | Yes          |
|                                | description                      | string                       | Description of the vulnerability                                                | Yes          |
|                                | severity                         | string (enum: low, medium, high, critical) | Severity level of the vulnerability                       | Yes          |
|                                | affected_files                   | array[string]                | List of file paths affected by the vulnerability                                | Yes          |
|                                | cve_reference                    | string                       | CVE reference for the vulnerability, if applicable                              | No           |
| **components**                 |                                  | array[object]                | Array of logical components in the codebase                                     | Yes          |
|                                | component_id                     | string                       | Unique identifier for the component                                             | Yes          |
|                                | component_name                   | string                       | Name of the component                                                           | Yes          |
|                                | description                      | string                       | Description of the component's purpose                                          | Yes          |
|                                | associated_files                 | array[string]                | List of file paths associated with the component                                | Yes          |
|                                | related_requirements              | array[string]                | List of requirement IDs related to the component                                | Yes          |
| **use_cases**                  |                                  | array[object]                | Array of user use cases supported by the codebase                               | Yes          |
|                                | use_case_id                      | string                       | Unique identifier for the use case                                              | Yes          |
|                                | use_case_name                    | string                       | Name of the use case                                                            | Yes          |
|                                | description                      | string                       | Description of the use case                                                     | Yes          |
|                                | associated_files                 | array[string]                | List of file paths involved in the use case                                     | Yes          |
|                                | involved_components              | array[string]                | List of component IDs involved in the use case                                  | Yes          |
| **functional_requirements**    |                                  | array[object]                | Array of functional requirements for the codebase                               | Yes          |
|                                | requirement_id                   | string                       | Unique identifier for the requirement                                           | Yes          |
|                                | text                             | string                       | Text description of the requirement                                             | Yes          |
|                                | implemented_by                   | array[string]                | List of file paths implementing the requirement                                 | Yes          |
| **data_details**               |                                  | object                       | Details about data-related aspects of the codebase                              | Yes          |
|                                | databases                        | array[object]                | List of databases used by the project                                           | Yes          |
|                                | databases.name                   | string                       | Name of the database                                                            | Yes          |
|                                | databases.type                   | string                       | Type of the database (e.g., MongoDB, PostgreSQL)                                | Yes          |
|                                | data_models                      | array[object]                | List of data models used in the project                                         | Yes          |
|                                | data_models.model_name           | string                       | Name of the data model                                                          | Yes          |
|                                | data_models.description          | string                       | Description of the data model                                                   | Yes          |
|                                | data_models.associated_files     | array[string]                | List of file paths defining or using the data model                             | Yes          |
|                                | api_endpoints                    | array[object]                | List of API endpoints provided by the project                                   | Yes          |
|                                | api_endpoints.path               | string                       | Path of the API endpoint                                                        | Yes          |
|                                | api_endpoints.method             | string                       | HTTP method of the endpoint (e.g., GET, POST)                                   | Yes          |
|                                | api_endpoints.description        | string                       | Description of the endpoint's functionality                                     | Yes          |
| **data_lineage**               |                                  | array[object]                | Array of data lineage entries describing data flow                              | Yes          |
|                                | lineage_id                       | string                       | Unique identifier for the data lineage entry                                    | Yes          |
|                                | source                           | string                       | Source of the data (e.g., database, user input)                                 | Yes          |
|                                | target                           | string                       | Target of the data (e.g., database, UI component)                               | Yes          |
|                                | transformation                   | string                       | Description of data transformation applied                                      | Yes          |
|                                | associated_use_case              | string                       | ID of the use case associated with the data flow                                | Yes          |

## Notes
- The schema adheres to JSON Schema Draft 2020-12 standards.
- The `checksum` property in `file_details` has a regex pattern (`^[a-fA-F0-9]{64}$`) to ensure a valid SHA-256 hash.
- The `severity` property in `security_vulnerabilities` is restricted to the enum values: "low", "medium", "high", "critical".
- All properties marked as "Required: Yes" are mandatory in their respective objects or arrays.
- Nested properties (e.g., `dependencies.name`, `databases.name`) are grouped under their parent sections for clarity.