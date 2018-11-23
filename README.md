# Simple secure file exchange

Very simple private file exchange written using Flask framework

## Features and limits

- All files stored encrypted, encryption key is a part of URL, but file name and mime type stored in plain text in extended attributes
- There's a limit on file size due to in-memory decryption
- File is deleted upon request, so URL is one-time use.
- Files with mime-type `image/*` will be displayed in browser, other types will be downloaded
- Plain text URL will be returned on request with no Referer, so it's useful in scripts:
  ```sh
  #!/bin/bash

  BASE_URL='<your url here>'

  url=$(curl -F "file=@requirements.txt" "https://${BASE_URL}/")
  echo $url

  url=$(echo test | curl -F "file=@-;filename=fun.txt" "https://${BASE_URL}/")
  echo $url
  ```
