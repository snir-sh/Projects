document.addEventListener('DOMContentLoaded', function() {
    // Replace delete checkboxes with trash icons in inline forms
    const deleteCheckboxes = document.querySelectorAll('input[name$="-DELETE"]');
    
    deleteCheckboxes.forEach(function(checkbox) {
        const row = checkbox.closest('.dynamic-form, tr');
        if (!row) return;
        
        // Create trash icon
        const trashIcon = document.createElement('span');
        trashIcon.innerHTML = '🗑️';
        trashIcon.style.cursor = 'pointer';
        trashIcon.style.fontSize = '18px';
        trashIcon.style.userSelect = 'none';
        trashIcon.setAttribute('data-delete-icon', 'true');
        
        // Replace checkbox with trash icon
        checkbox.parentNode.replaceChild(trashIcon, checkbox);
        
        // Add click handler
        trashIcon.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (confirm('Are you sure you want to remove this user from the group?')) {
                // Create hidden checkbox and check it
                const hiddenCheckbox = document.createElement('input');
                hiddenCheckbox.type = 'hidden';
                hiddenCheckbox.name = checkbox.name;
                hiddenCheckbox.value = 'on';
                row.appendChild(hiddenCheckbox);
                
                // Mark row as deleted
                row.style.display = 'none';
                
                // If this is a new empty row, remove it completely
                if (row.classList.contains('empty-form')) {
                    row.remove();
                }
            }
        });
    });
});
