([url, filename]) => {
  async function createDownloadAnchorFor(url, filename=null) {
    let downloadsContainer = document.querySelector('.downloads-container');
    if (!downloadsContainer) {
      downloadsContainer = document.createElement('div');
      downloadsContainer.style = "display: initial; left: 0px; top: 0px; font-family: monospace;";
      downloadsContainer.style.position = "fixed";
      downloadsContainer.classList.add('.downloads-container');
      document.body.appendChild(downloadsContainer);
    }
    
    let a = document.createElement('a');

    a.setAttribute("target", '_blank');
    a.setAttribute("download", '');
    a.textContent = "download";
    a.id = "download-" + Date.now();

    if (filename != null) {
      a.setAttribute('download', filename)
    }
    
    let blob = await fetch(url).then(r => r.blob());
    let blobUrl = URL.createObjectURL(blob);
    a.href = blobUrl;

    downloadsContainer.appendChild(a);

    return a.id;
  }

  return createDownloadAnchorFor(url, filename);
}