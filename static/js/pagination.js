function paginateBookContent() {
  const flipbook = document.querySelector('.flipbook');

  const frontCover = flipbook.querySelector('article.page.cover.hard:first-child')?.cloneNode(true);
  const backCover = flipbook.querySelector('article.page.cover.hard:last-child')?.cloneNode(true);

  const originalPage = flipbook.querySelector('article.page:not(.cover)');
  if (!originalPage) return;

  const originalContentHTML = originalPage.querySelector('.pagestyle')?.innerHTML || '';

  // Parse content into individual elements
  const parser = document.createElement('div');
  parser.innerHTML = originalContentHTML;
  const elements = Array.from(parser.childNodes);

  // Measurement container
  const tempPage = document.createElement('div');
  tempPage.style.width = '440px';
  tempPage.style.height = '550px';
  tempPage.style.position = 'absolute';
  tempPage.style.visibility = 'hidden';
  tempPage.style.overflow = 'hidden';
  tempPage.style.padding = '20px';
  tempPage.style.fontSize = '0.7rem';
  tempPage.style.boxSizing = 'border-box';
  tempPage.style.lineHeight = '1.4';
  tempPage.className = 'pagestyle';
  document.body.appendChild(tempPage);

  const maxHeight = tempPage.clientHeight;

  let pages = [];
  let currentPage = document.createElement('div');
  currentPage.className = 'pagestyle';

  elements.forEach((el) => {
    const clone = el.cloneNode(true);

    currentPage.appendChild(clone);
    tempPage.innerHTML = currentPage.innerHTML;

    if (tempPage.scrollHeight > maxHeight) {
      currentPage.removeChild(clone);
      pages.push(currentPage.innerHTML);
      currentPage = document.createElement('div');
      currentPage.className = 'pagestyle';
      currentPage.appendChild(clone);

      tempPage.innerHTML = currentPage.innerHTML;
      if (tempPage.scrollHeight > maxHeight) {
        pages.push(currentPage.innerHTML);
        currentPage = document.createElement('div');
        currentPage.className = 'pagestyle';
      }
    }
  });

  if (currentPage.childNodes.length > 0) {
    pages.push(currentPage.innerHTML);
  }

  document.body.removeChild(tempPage);

  // Rebuild flipbook
  flipbook.innerHTML = '';
  if (frontCover) flipbook.appendChild(frontCover);

  pages.forEach((html, index) => {
    const article = document.createElement('article');
    article.className = 'page';

    const inner = document.createElement('div');
    inner.className = 'pagestyle';
    inner.innerHTML = html;

    // Add page number
    const pageNumber = document.createElement('div');
    pageNumber.className = 'page-number';
    pageNumber.textContent = `( ${index + 1} )`;
    inner.appendChild(pageNumber);

    article.appendChild(inner);
    flipbook.appendChild(article);
  });

  if (backCover) flipbook.appendChild(backCover);
}


    // Call function after DOM is loaded
    window.addEventListener('DOMContentLoaded', paginateBookContent)