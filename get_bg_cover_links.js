
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
  
  /*
  scrollListener = event => {
    if (reachedScrollEndOf(event.target)) {
      console.log('scroll end');
      scrollEnd = true;
      pageScrollElement.removeEventListener('scroll', scrollListener);
    } else {
      console.log("scrolling...");
    }
  }

  pageScrollElement.addEventListener('scroll', scrollListener);

  */

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

  // bgCover = Array.from(bgCoversSet.values()).at(-1)

  // regex = /url\("([^"]+)"\)/g;

  res = Array.from(bgCoversSet.values()).map((el) => ({href:el.href, style:el.style.backgroundImage}));
  console.log(res);
  return res;

})();

