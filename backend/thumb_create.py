import Image
import sys
import os.path
from subprocess import call

thumb_size = 96, 96
orig_size = 640, 480

basedir = os.path.abspath(os.path.dirname(__file__))
orig_dir = os.path.join(basedir, 'app/static/tmp/')
thumb_dir = os.path.join(basedir, 'app/static/thumb/')
img_dir = os.path.join(basedir, 'app/static/large/')
if len(sys.argv) > 1:
    sysinput = sys.argv[1].lower()
    input_img = orig_dir + sysinput + '.jpg'
    thumb_img = thumb_dir + sysinput +'.jpg'
    large_img = img_dir + sysinput + '.jpg'
    try:
    	im = Image.open(input_img)
    	im.thumbnail(thumb_size, Image.ANTIALIAS)
    	im.save(thumb_img,'JPEG')
    	print 'thumbnail saved'
    except IOError:
    	print 'thumbnail image upload failed'

    try:
    	im = Image.open(input_img)
    	im.thumbnail(orig_size, Image.ANTIALIAS)
    	im.save(large_img,'JPEG')
    	print 'full image saved'
    except IOError:
    	print 'image upload failed'

    call(['rm', input_img])




