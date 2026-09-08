(function () {
  function toggleQuestionFields() {
    var typeSelect = document.getElementById('id_question_type');
    if (!typeSelect) {
      return;
    }

    var selectedType = typeSelect.value;

    var usesOptions = selectedType === 'choice' || selectedType === 'multi_select';
    var fieldVisibility = {
      choices: usesOptions,
      max_selections: selectedType === 'multi_select',
      multi_text_count: selectedType === 'multi_text'
    };

    Object.keys(fieldVisibility).forEach(function (fieldName) {
      var field = document.getElementById('id_' + fieldName);
      if (!field) {
        return;
      }

      var row = field.closest('.form-row');
      if (!row) {
        return;
      }

      row.style.display = fieldVisibility[fieldName] ? '' : 'none';
    });

    var optionInlineGroup = document.getElementById('questionoption_set-group');
    if (optionInlineGroup) {
      optionInlineGroup.style.display = usesOptions ? '' : 'none';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var typeSelect = document.getElementById('id_question_type');
    if (!typeSelect) {
      return;
    }

    toggleQuestionFields();
    typeSelect.addEventListener('change', toggleQuestionFields);
  });
})();
