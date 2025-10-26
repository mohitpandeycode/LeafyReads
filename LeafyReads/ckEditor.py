
customColorPalette = [
    {'color': 'hsl(0, 0%, 0%)', 'label': 'Black'},
    {'color': 'hsl(0, 0%, 30%)', 'label': 'Dim grey'},
    {'color': 'hsl(0, 0%, 60%)', 'label': 'Grey'},
    {'color': 'hsl(0, 0%, 90%)', 'label': 'Light grey'},
    {'color': 'hsl(0, 0%, 100%)', 'label': 'White'},
    {'color': 'hsl(0, 75%, 60%)', 'label': 'Red'},
    {'color': 'hsl(0, 75%, 30%)', 'label': 'Dark red'},
    {'color': 'hsl(30, 75%, 60%)', 'label': 'Orange'},
    {'color': 'hsl(30, 75%, 30%)', 'label': 'Dark orange'},
    {'color': 'hsl(60, 75%, 60%)', 'label': 'Yellow'},
    {'color': 'hsl(60, 75%, 30%)', 'label': 'Dark yellow'},
    {'color': 'hsl(100, 75%, 60%)', 'label': 'Light green'},
    {'color': 'hsl(100, 75%, 30%)', 'label': 'Dark green'},
    {'color': 'hsl(135, 75%, 60%)', 'label': 'Green'},
    {'color': 'hsl(135, 75%, 30%)', 'label': 'Dark green'},
    {'color': 'hsl(165, 75%, 60%)', 'label': 'Cyan'},
    {'color': 'hsl(165, 75%, 30%)', 'label': 'Dark cyan'},
    {'color': 'hsl(195, 75%, 60%)', 'label': 'Light blue'},
    {'color': 'hsl(195, 75%, 30%)', 'label': 'Dark blue'},
    {'color': 'hsl(225, 75%, 60%)', 'label': 'Blue'},
    {'color': 'hsl(225, 75%, 30%)', 'label': 'Dark blue'},
    {'color': 'hsl(270, 75%, 60%)', 'label': 'Purple'},
    {'color': 'hsl(270, 75%, 30%)', 'label': 'Dark purple'},
    {'color': 'hsl(300, 75%, 60%)', 'label': 'Light purple'},
    {'color': 'hsl(300, 75%, 30%)', 'label': 'Dark purple'}
]

# CKEDITOR_5_FILE_STORAGE = "path_to_storage.CustomStorage" # optional
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'link', 'blockQuote', 'code', 'codeBlock', '|',
                'bulletedList', 'numberedList', 'todoList', '|',
                'outdent', 'indent', '|',
                'imageUpload', 'insertImage', 'insertTable', 'mediaEmbed', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
                'alignment', 'horizontalLine', 'pageBreak', 'specialCharacters', '|',
                'removeFormat', 'undo', 'redo'
            ],
            'shouldNotGroupWhenFull': True,
        },
        'height': 400,
        'width': '100%',
    },

    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList', 'todoList',
            '|',
            'blockQuote',
        ],

        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough',
                'subscript', 'superscript', 'highlight', '|',
                'code', 'codeBlock', 'sourceEditing', '|',
                'link', 'blockQuote', '|',
                'bulletedList', 'numberedList', 'todoList', 'outdent', 'indent', '|',
                'insertImage', 'imageUpload', 'insertTable', 'mediaEmbed', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
                'alignment', 'horizontalLine', 'pageBreak', 'specialCharacters', '|',
                'selectAll', 'removeFormat', 'undo', 'redo'
            ],
            'shouldNotGroupWhenFull': True,
        },

        'mediaEmbed': {
            'previewsInData': True,
        },

        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:alignLeft', 'imageStyle:alignCenter',
                'imageStyle:alignRight', 'imageStyle:side'
            ],
            'styles': [
                'full', 'side', 'alignLeft', 'alignRight', 'alignCenter'
            ],
        },

        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties'
            ],
            'tableProperties': {
                'borderColors': customColorPalette,      # your palette used directly
                'backgroundColors': customColorPalette,
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette,
            },
        },

        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
            ],
        },
    },

    'list': {
        'properties': {
            'styles': True,
            'startIndex': True,
            'reversed': True,
        }
    }
}
