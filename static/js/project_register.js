document.getElementById('add-item-button').addEventListener('click', function(event) {
		event.preventDefault(); // フォームの送信を防止

		// 新しい入力フォームを作成
		const newInputDiv = document.createElement('div');
		newInputDiv.classList.add('form-item');

		const newInput = document.createElement('input');
		newInput.type = 'text';
		newInput.id="item-name";
		newInput.name = 'item-name';
		newInput.autocomplete = 'off';
		newInput.maxLength = 64;
		newInput.required = true;

		// 新しい入力フォームをdivに追加
		newInputDiv.appendChild(newInput);

		// フォームコンテナに新しい入力フォームを追加
		document.getElementById('form-container').appendChild(newInputDiv);
});
