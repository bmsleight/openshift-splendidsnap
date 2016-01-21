from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import sys
sys.path.append('./')

from appsplendid.models import Splendid, PDFS
import _libspendidsnap, _tweetss, random, shutil, glob, os

class Command(BaseCommand):
#    args = '<poll_id poll_id ...>'
    help = 'Makes PDF where one does not exist'

    def handle(self, *args, **options):
        packs = Splendid.objects.filter(pdf="")
        if packs:
            pack = packs[0]
            self.stdout.write('Pack 1: "%s"' % pack)
            if not os.path.exists(settings.MEDIA_ROOT + PDFS):
                os.makedirs(settings.MEDIA_ROOT + PDFS)
            store_root = settings.MEDIA_ROOT  
            pdf_mid = PDFS + "/" + pack.pack_name + "_by_" + pack.creator + "_" + str(pack.id)
            pdf_shortfile = pdf_mid + ".pdf"
            showcase_short = pdf_mid + ".png"
            pdf_name = store_root + pdf_shortfile
            showcase = store_root + showcase_short
            texts = []
            images = []
            text_images = []
            image_zip_name = ""
            if pack.words:
                texts = pack.words.strip().split(',')
                texts = filter(None, texts)
                text_images = _libspendidsnap.list_of_images_from_text(texts)
                images = text_images
            if pack.image_zip_file:
                image_zip_name = pack.image_zip_file.name
                tmp_imagesdir = _libspendidsnap.unpack_flat(pack.image_zip_file)
                images = images + glob.glob(tmp_imagesdir + '/*')
            self.stdout.write('Texts: "%s"' % texts)
            self.stdout.write('Images: "%s"' % images)
            self.stdout.write('Zip file: "%s"' % str(image_zip_name))


            arrangements, total_needed = _libspendidsnap.simple_card_list(pack.images_per_card-1)
            random.shuffle(images)
            #Now add the mandatory images - after the random shuffle
            if pack.free:
                free_texts = ['SplendidSnap.com', 'Free\\nVersion', '\@SplendidSnap']
                free_images = _libspendidsnap.list_of_images_from_text(free_texts)
                text_images = text_images + free_images
                # Add at start so they have to be included
                images = free_images + images
            
            num_images = len(images)
            while total_needed > num_images:
                tmp_list = []
                tmp_list.append(str(num_images))
                tmp_list_images = _libspendidsnap.list_of_images_from_text(tmp_list)
                text_images = text_images + tmp_list_images
                images = images + tmp_list_images 
                num_images = len(images)
            real_pack = _libspendidsnap.Pack(images[:total_needed])
            for arrangement in arrangements:
                real_pack.make_card(arrangement)

            _libspendidsnap.generate__a4_pdf_from_images_list(images_filenames_list=real_pack.cards, 
                                                              pdf_name=pdf_name,
                                                              pack_name = pack.pack_name,
                                                              creator = pack.creator,
                                                              images_per_card =pack.images_per_card,
                                                              word_list = texts,
                                                              image_zip_name = image_zip_name,
                                                              source_of_images = pack.source_of_images,
                                                              
)
            _libspendidsnap.showcase_image(real_pack.cards, showcase=showcase)
            pack.pair_image = showcase_short
            pack.pdf = pdf_shortfile
            pack.save()
            _libspendidsnap.clean_up(real_pack.cards + real_pack.list_of_thumbs() + real_pack.images_filenames_list)
            if text_images:
                _libspendidsnap.clean_up(text_images)
            if pack.image_zip_file:
                shutil.rmtree(tmp_imagesdir)
            tweet = pack.pack_name + ' by @' + pack.creator + ' Download the full pack - http://SplendidSnap.com/appsplendid (' + str(pack.id) + ')'
            print (showcase, tweet )
            _tweetss.tweet(showcase, tweet)
       
            # cleanup
            _libspendidsnap.clean_up(real_pack.cards + real_pack.list_of_thumbs() + real_pack.images_filenames_list)
            _libspendidsnap.clean_up(text_images)
            if pack.image_zip_file:
                shutil.rmtree(tmp_imagesdir)



