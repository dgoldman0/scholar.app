const toggleBtn = document.getElementById('toggleBtn');
const codePane  = document.getElementById('codePane');
const renderPane = document.getElementById('renderPane');
let showingRender = false;

toggleBtn.addEventListener('click', () => {
  showingRender = !showingRender;
  if(showingRender){
    codePane.style.display = 'none';
    renderPane.style.display = 'block';
    toggleBtn.textContent = 'LaTeX';
  }else{
    codePane.style.display = 'block';
    renderPane.style.display = 'none';
    toggleBtn.textContent = 'Render';
  }
});
