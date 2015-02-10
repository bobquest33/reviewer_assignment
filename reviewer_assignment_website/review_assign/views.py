from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import RequestContext

from ajaxuploader.views import AjaxFileUploader
from review_assign.forms import SubmitAssingmentInformation
from django.views.generic import FormView
from django.http import HttpResponseRedirect
from django.core.files.base import ContentFile
import django_tables2 as tables
from django.core.urlresolvers import reverse
import pandas as pd

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import uuid


def get_file_path(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

class index(FormView):
    template_name = 'review_assign/submit.html'
    form_class = SubmitAssingmentInformation

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            # process files, create random names, and save to temporary folder
            people_fn = get_file_path(str(request.FILES['people']))
            # save files
            default_storage.save(os.path.join('tmp', people_fn),
                                 ContentFile(request.FILES['people'].read()))
            article_info_fn = get_file_path(str(request.FILES['article_information']))
            default_storage.save(os.path.join('tmp', article_info_fn),
                                 ContentFile(request.FILES['article_information'].read()))
            try:
                reviewers_fn = get_file_path(str(request.FILES['reviewers']))
                default_storage.save(os.path.join('tmp', reviewers_fn),
                                     ContentFile(request.FILES['reviewers'].read()))
            except Exception:
                reviewers_fn = None

            try:
                coi_fn = get_file_path(str(request.FILES['coi']))
                default_storage.save(os.path.join('tmp', coi_fn),
                                     ContentFile(request.FILES['coi'].read()))
            except Exception:
                coi_fn = None

            min_rev_art = request.POST['minimum_reviews_per_article']
            max_rev_art = request.POST['maximum_reviews_per_article']
            min_art_rev = request.POST['minimum_articles_per_reviewer']
            max_art_rev = request.POST['maximum_articles_per_reviewer']

            return HttpResponseRedirect(reverse('result', args=(),
                                                kwargs={'people_fn': people_fn,
                                                        'article_info_fn': article_info_fn,
                                                        'reviewers_fn': reviewers_fn,
                                                        'coi_fn': coi_fn,
                                                        'min_rev_art': min_rev_art,
                                                        'max_rev_art': max_rev_art,
                                                        'min_art_rev': min_art_rev,
                                                        'max_art_rev': max_art_rev}))
        else:
            return self.form_invalid(form)


class PeopleTable(tables.Table):
    PersonID = tables.Column(verbose_name='ID')
    FullName = tables.Column(verbose_name='Full name')


def result(request, people_fn=None, article_info_fn=None, reviewers_fn=None, coi_fn=None,
           min_rev_art=None, max_rev_art=None, min_art_rev=None, max_art_rev=None):
    # read file
    people_path = os.path.join(settings.MEDIA_ROOT, os.path.join('tmp', people_fn))
    people_data = pd.DataFrame.from_csv(people_path, index_col=None)
    article_path = os.path.join(settings.MEDIA_ROOT, os.path.join('tmp', article_info_fn))
    article_data = pd.DataFrame.from_csv(article_path, index_col=None)

    if reviewers_fn is not None:
        reviewers_path = os.path.join(settings.MEDIA_ROOT, os.path.join('tmp', reviewers_fn))
        reviewers_data = pd.DataFrame.from_csv(reviewers_path, index_col=None)

    if coi_fn is not None:
        coi_path = os.path.join(settings.MEDIA_ROOT, os.path.join('tmp', coi_fn))
        coi_data = pd.DataFrame.from_csv(coi_path, index_col=None)

    people_table = PeopleTable(people_data.to_dict('records'))
    return render_to_response('review_assign/result.html', {"people": people_table},
                              context_instance=RequestContext(request))



import_uploader = AjaxFileUploader()