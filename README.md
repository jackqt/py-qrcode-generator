# Introduction


# Usage
## Command Line
To use this library, please give 2 parameters at lease, for example:
```
python app/run.py inner_logo_path qr_content [width] [height]
```
*Note:* The 1st param `inner_logo_path` could be absolute local path, or a URL

Finally, qrcode image(with `.png` name) will be save to currently execution folder

## In Python Code
Just follow this snippet to integrate with your code
```
from QRCodeConverter import QRCodeConverter
# ...
converter = QRCodeConverter()
converter.set_inner_img_path(parser['img_path'])
converter.set_qrcode_content(parser['content'])
converter.set_qrcode_size(parser['size'])
qrcode_img_path = converter.process()
```
The _process_ function also receive two callback function for invoke after save
the qrcode into local path

# Known Issue
+ Does not handle the case if do not give `inner_logo_path` in the command line
+ Param `content` should be mandatory
