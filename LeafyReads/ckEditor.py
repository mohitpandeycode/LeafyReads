
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
            'items': ['heading', '|', 'bold', 'italic', 'link',
                      'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
                    }

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': {
            'items': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                      'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',
                    ],
            'shouldNotGroupWhenFull': 'true'
        },
        'mediaEmbed': {
            'previewsInData': True,
            'extraProviders': [
                {
                    'name': 'youtube',
                    'url': r'^https?://(www\.)?youtube\.com/watch\?v=.+',
                    'html': '<div class="video-container"><iframe src="{url}" frameborder="0" allowfullscreen></iframe></div>'
                },
                {
                    'name': 'vimeo',
                    'url': r'^https?://(www\.)?vimeo\.com/.+',
                    'html': '<div class="video-container"><iframe src="{url}" frameborder="0" allowfullscreen></iframe></div>'
                }
            ]
        },

        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
