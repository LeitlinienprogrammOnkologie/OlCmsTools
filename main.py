from ContentFinder import ContentFinder

#keyword_list = ['follow-up', 'aftercare', 'aftertreatment', 'after-care', 'postoperative care', 'post-operative care', 'Nachsorge', 'Nachfürsorge', 'Postvention']
keyword_list = ['Forschungsfrage', 'Forschungsbedarf']

content_finder = ContentFinder()
#content_finder.Find(keyword_list)
content_finder.FindByGuidelineHierarchy(keyword_list)