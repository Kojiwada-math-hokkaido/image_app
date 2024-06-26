document.getElementById('add-item-button').addEventListener('click', function(event) {
		event.preventDefault(); // フォームの送信を防止

		// 新しい入力フォームを作成
		const newInputDiv = document.createElement('div');
		newInputDiv.classList.add('form-item');

		const newInputLabel = document.createElement('label');
		newInputLabel.textContent = '項目名：';

		const newInput = document.createElement('input');
		newInput.type = 'text';
		newInput.name = 'item-name';
		newInput.autocomplete = 'off';
		newInput.maxLength = 64;
		newInput.required = true;

		// 新しい入力フォームをdivに追加
		newInputDiv.appendChild(newInputLabel);
		newInputDiv.appendChild(newInput);

		// フォームコンテナに新しい入力フォームを追加
		document.getElementById('form-container').appendChild(newInputDiv);
});
