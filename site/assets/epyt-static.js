/*
 * Static stand-in for the YouTube Embed Plus gallery paging request.
 *
 * On WordPress, the gallery's "Next »" and "« Prev" buttons asked
 * wp-admin/admin-ajax.php for the next page of thumbnails.  Every page of
 * both galleries was saved on 24 November 2026 as
 * epyt-pages/<playlistId>/<pageToken>.html (the first page as first.html).
 * This script answers the plugin's request from those files, so the gallery
 * looks and behaves exactly as before.  Nothing visible is changed.
 *
 * If a playlist gains videos on YouTube, re-save its pages (see
 * tools/mirror_build.py) or the gallery will keep showing the saved set.
 */
(function () {
  var me = document.currentScript && document.currentScript.src || '';
  var base = me.replace(/assets\/epyt-static\.js(\?.*)?$/, '');
  var $ = window.jQuery;
  if (!$ || !base) return;
  var post = $.post;
  $.post = function (url, data, done) {
    if (data && data.action === 'my_embedplus_gallery_page') {
      var o = data.options || {};
      var file = base + 'epyt-pages/' + encodeURIComponent(o.playlistId) + '/' +
                 encodeURIComponent(o.pageToken || 'first') + '.html';
      return $.get(file, done, 'html');
    }
    return post.apply(this, arguments);
  };
})();
