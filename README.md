# Hex Dominion legal pages

Privacy policy of Hex Dominion, published at <https://hex-dominion.hirantravassos.com.br/>. The pages are generated from
`docs/store/privacy-policy` of the game repository (`tools/build_store_documents.ps1`) and copied here.

* The version of the site is in `VERSION` and shown at the bottom of every page ("Site version").
* `python scripts/check_site.py` runs the checks (also run by the workflow `quality`).
* Open a pull request, wait for **quality**, merge: the merge publishes the site (the deploy job needs the quality job).
  The branch is deleted after the merge. `main` and the `vX.Y.Z` tags are the only long-lived refs.
