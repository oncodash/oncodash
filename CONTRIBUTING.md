
Thank you for considering contributing to Oncodash.
We value your time in helping us to improve the life of medical practitionners
and patients who fight against cancers.


Introduction
============

Most of the following guidelines are here to help the contributers to reduce
(a bit) the burden of managing and developing this open-source project.
Our main objective is to help newcomers to communicate efficiently with
maintainers.

There are many ways to contribute, from writing tutorials or blog posts,
improving the documentation, submitting bug reports and feature requests,
or writing code which can be incorporated into Oncodash itself.

Following these guidelines helps to communicate that you respect the time of the developers.
In return, they should reciprocate that respect in addressing your issue, assessing changes,
and helping you finalize your pull requests.

The following suggestions are *guidelines*, not *rules*,
which means that we would prefer you to actually submit something,
even if you don't completely follow all of them.
If you don't know how to follow some of those guidelines, do not hesitate to
submit your contribution and add a comment about your difficulties.


How to Report a Bug
===================

If you find a *security vulnerability*, do **NOT** open an issue.
Email [johann.dreo@pasteur.fr](mailto:johann.dreo@pasteur.fr) instead.

Before posting a new bug, please ensure that there is no previous issue
addressing the same problem.
To do that, go on the [issues](https://github.com/oncodash/oncodash/issues?q=is%3Aissue)
tab of the project and search for all (open or closed) issues.

When filing a report, make sure to answer these five questions:

- What version of Oncodash are you using?
    - If you use a release, indicate its tag, else indicate the specific commit hash. 
- What operating system are you using?
- What versions of Docker, Python and Typescript?
- What did you do?
    - Explain the steps to reproduce the bug from a fresh start.
- What did you expect to see?
- What did you see instead?


How to Submit Code
==================

1. Create your own fork of the project.
2. Checkout the `develop` branch.
3. Checkout a branch named after the following convention:
    - `<type>[#:ID]_[scope/]<three-keywords-max>`
    - `type` may be: `feat`, `fix`, `doc`, `refactor`, `build`, `ci`, etc.
    - `ID` (optional) refers to the issue number.
    - `scope` is a generic category, like "frontend", "backend" or "widget".
    - Examples: `feat_widget/timeline` or `fix#12_backend/import-clinical`
4. Commit your changes using the [Conventional Commits](https://www.conventionalcommits.org/) convention:
    - First line: `<type>[(scope)][!]: <short description>`,
      the exclamation mark indicating a breaking change (usually in an API).
    - Empty line, followed by a multi-line long description.
    - Optional footer as `Ref:#<ID>` on separate line(s), to [reference a related issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
      or explain the breaking change.
    - Example:
        ```
        fix(API)!: use dictionary instead of list in inference server

        This should improve performances by allowing queries in O(log n) instead of O(n).

        Ref:#123
        BREAKING CHANGE: expects a key-value pair instead of single items.
        ```
    - If you spread your changes across several atomic commits,
      in order to ease the reviewer's job (thanks!),
      please ensure that at least one commit message is correctly formatted with
      all relevant information.
5. Ensure that you did not introduce bugs by adding unit tests that run your new code.
6. Ensure that you did not introduced a regression by running all the tests
   yourself, from within the project's containers.
7. Add explanations about your new feature in the documentation.
8. Push on your own repository and click on the "Create pull request" green
   button that should appear on your fork's page (or go to the original
   project page and click on "[Pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)").
   If you would like to get feedback but your code is not yet ready for merging, create a draft pull request instead. Please ensure you are doing so against the `develop` branch.
9. In the "base" dropdown menu, select the "dev" branch.


How to Merge code
=================

Our policiy for merging pull requests is to squash all commits into one.
It is fine if your pull request consists in several commits,
especially if you made them atomic, so as to ease the review.
Note that we will squash your commits into a single one for the merge.

In any case, enabling the checkbox
"[allow maintainer edits](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork)"
may help going faster through the review process.

Your pull request will soon be reviewed by our developers.
We may take time to do so.
If you feel that we take too much time, do not hesitate to
ask for a review ("Reviewers" in the right sidebar)
or to post a comment under your pull request, asking for an update.

As you update your pull request, following the reviewers' suggestions,
do not forget to apply changes and mark each conversations as
"[resolved](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/commenting-on-a-pull-request#resolving-conversations)".

