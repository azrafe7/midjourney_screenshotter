
(async () => {

  maxAttempts = 1000;
  selector = '.bg-cover';
  bgCoversSet = new Set();
  links = [];

  pageScrollElement = document.querySelector('#pageScroll');

  // scrollEnd = false;

  reachedScrollEndOf = (elem) => {
    const {scrollHeight, scrollTop, clientHeight} = elem;

    if (Math.abs(scrollHeight - clientHeight - scrollTop) < 10) {
      console.log('reached scroll end');
      return true;
    } else {
      return false;
    }
  }

  function smoothScrollBy(elem, offset=0) {
    elem.scrollBy({
      top: offset,
      behavior: 'smooth'
    });

    return new Promise((resolve, reject) => {
      const failed = setTimeout(() => {
        elem.removeEventListener("scrollend", scrollEndHandler);
        reject();
      }, 2000);

      const scrollEndHandler = () => {
        elem.removeEventListener("scrollend", scrollEndHandler);
        clearTimeout(failed);
        resolve();
      };

      elem.addEventListener("scrollend", scrollEndHandler);
    });
  }

  while (!reachedScrollEndOf(pageScrollElement) && maxAttempts >= 0) {
    await smoothScrollBy(pageScrollElement, 200).then(() => {
      bgCovers = Array.from(document.querySelectorAll(selector));
      for (bgCover of bgCovers) {
        bgCoversSet.add(bgCover);
      }
    });
    maxAttempts--;
  }

  console.log(`bgCoversSet.size: ${bgCoversSet.size}`);

  url_regex = /url\("([^"]+)"\)/g;

  bgCovers = Array.from(bgCoversSet.values());
  
  res = bgCovers.map((el, idx) => {
    backgroundImageStyle = el.style.backgroundImage;
    matches = [...backgroundImageStyle.matchAll(url_regex)];
    matched_urls = matches.map((m) => m.length > 1 ? m[1] : [])
    return {idx:idx, href:el.href, style:backgroundImageStyle, urls:matched_urls};
  });
  
  console.log(res);

  // append dummy textarea
  textAreaElement = document.createElement('textarea');
  textAreaElement.id = '__hidden_bg_text_area';
  textAreaElement.style = "display: none; right: 0px; bottom: 0px; width: 600px; height: 300px; font-family: monospace;";
  textAreaElement.textContent = JSON.stringify(res);
  // Prevent scrolling to bottom of page in MS Edge
  textAreaElement.style.position = "fixed";
  
  document.body.appendChild(textAreaElement);

  return res;

})();
