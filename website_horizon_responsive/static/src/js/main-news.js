/* global $, moment */

$(document).ready(function(){
    const RSS_URL = `https://horizon-dev.student-crlg.be/feed/feed.xml`;

    $.ajax(RSS_URL, {
      accepts: {
        xml: "application/rss+xml"
      },
    
      dataType: "xml",
    
      success: function(data) {
        $(data)
          .find("item")
          .each(function() {
            const el = $(this);
    
            const template = `
              <article class='mb-4'>
                <h6>
                  <a href="${el
                    .find("link")
                    .text()}" target="_blank" rel="noopener">
                    ${el.find("title").text()}
                  </a>
                </h6>
                <img src="${$($.parseHTML(el.find('content\\:encoded').text())).find('img').attr('src')}" alt="" class='mb-2'>
                <span>${el.find("description").text()}</span>
              </article>
            `;
    
            $('#crlg_news').append(template);
          });
      }
    });
      
});