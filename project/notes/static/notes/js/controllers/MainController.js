var MainController = function($http, $scope) {

    var that = this;

    this.isPreload = false;
    this.countPreload = 0;

    this.url = {
        server: 'http://127.0.0.1:8000/',
        dropbox: {
            getMetaFiles: 'dropbox/get_meta_files/',
            getNotesFast: 'dropbox/get_notes_final/',
            getNotesSlow: 'dropbox/get_notes_alt/',
            addDelNotes: 'dropbox/add_or_del_meta_files/',
            createEditNote: 'dropbox/create_or_edit_note/',
            format_to_date: 'dropbox/format_to_date/',
            change_meta_note: 'dropbox/change_meta_note/',
            uploadFile: 'dropbox/upload_file/',
            downloadFile: 'dropbox/download_file'
        },

        getFullPath: function(path) {
            return this.server + eval('this.' + path);
        }
    }

    this.images = {
        formats: {
            'application/vnd.ms-excel': 'excel.png',
            'application/pdf': 'pdf.png',
            'application/vnd.ms-powerpoint': 'powerpoint.png',
            'application/msword': 'word.png',
            'text': 'text.png',
            'image': 'any_image_type.png'
        },

        getImageByFormat: function(contentType) {
            var content = contentType.split('/')[0];
            var type = contentType.split('/')[1];

            switch (content) {
                case 'text':
                    return 'text.png';
                case 'image':
                    return 'any_image_type.png';
                case 'application':
                    switch (type) {
                        case 'vnd.ms-excel':
                            return 'excel.png';
                        case 'pdf':
                            return 'pdf.png';
                        case 'vnd.ms-powerpoint':
                            return 'powerpoint.png';
                        case 'msword':
                            return 'word.png';
                        default:
                            return 'default.png';
                    }
                default:
                    return 'default.png';
            }
        }
    }

    this.user = {
        projects: '',
        tags: '',
        file: '',
        notes: {
            order: {
                full_info: '',
                form_date: ''
            },
            clear: '',
        },
        choices: {
            projects: '',
            tags: '',
            errors: {
                projects: '',
                tags: ''
            },
        },
        create: {
            text: '',
            tag: 'tag',
            project: 'notebook'
        }
    }

    this.messages = {
        success: {
            settings: ''
        }
    }

    this.filters = {
        projects: 'notebook',
        tags: 'tag'
    }

    this.timeliner = {
        date: '',
        current_list: [],
    }

    this.downloadFile = function(path) {
        var req = {
            method: 'GET',
            url: that.url.getFullPath('dropbox.downloadFile'),
            params: {
                path: path,
            }
        }
        $http(req).success(function() {
            alert('succ')
        });
    }

    this.createNote = function() {
        var req = {
            method: 'POST',
            url: this.url.getFullPath('dropbox.createEditNote'),
            data: {
                'text': that.user.create.text,
                'project': that.user.create.project,
                'tag': that.user.create.tag,
                'action': 'create'
            }
        };

        $http(req).success(function(data) {
            that.user.create.text = '';
            that.user.create.tag = 'tag';
            that.user.create.project = 'notebook';
            that.user.notes.order.full_info.push(data['obj']);
            that.user.notes.clear.push(data['obj'].path);

            var loc_req = {
                method: 'POST',
                url: that.url.getFullPath('dropbox.format_to_date'),
                data: {
                    new_note: data['obj'],
                    notes: that.user.notes.order.form_date
                }
            };
            $http(loc_req).success(function(data) {
                that.user.notes.order.form_date = data['notes'];
            });
        });
    }

    this.changeMeta = function(path, type, meta_name) {
        var req = {
            method: 'GET',
            url: that.url.getFullPath('dropbox.change_meta_note'),
            params: {
                path: path,
                type: type,
                meta_name: meta_name
            }
        }
        $http(req).success(function(data) {
            that.changeMetaAngular(type, path, meta_name);
        });
    }

    $scope.sendFileAjax = function() {
        var path = this.note.path;
        var fd = new FormData();
        fd.append("file", $("input[data-file='file_" + path + "']")[0].files[0]);
        fd.append("path", path);

        url = that.url.getFullPath('dropbox.uploadFile');

        $http.post(url, fd, {
            headers: {'Content-Type': undefined },
            transformRequest: angular.identity
        }).success(function(data) {
            var notes = that.user.notes.order.full_info
            for (var i = 0; i < notes.length; i++) {
                if (notes[i].path == path) {
                    notes[i].files.push(data['res'])
                }
            }
        })
    }

    this.changeMetaAngular = function(type, path, new_val) {
        notes_all_info = that.user.notes.order.full_info
        for (var i=0; i < notes_all_info.length; i++) {
            if (notes_all_info[i].path === path) {
                var targetNote = notes_all_info[i],
                    old_path = targetNote.path.split('/'),
                    old_name = old_path[old_path.length-1].split('_');

                if (type === 'project') {
                    var index = 1;
                    targetNote.project = new_val;
                } else if (type === 'tag') {
                    var index = 2;
                    targetNote.tag = new_val;
                }
                old_name[index] = new_val;

                var new_name = old_name.join('_');
                old_path[old_path.length-1] = new_name;

                var new_path = old_path.join('/');
                targetNote.path = new_path;

            }
        }
    }

    this.selectFile = function(path){
         $("input[data-file='file_" + path + "']").click();
    }


    this.changeDate = function(user_date) {
        all_notes = that.user.notes.order.full_info;
        var find_index = null;
        for (var i = 0; i < all_notes.length; i++) {
            if (user_date == all_notes[i].path) {
                find_index = i;
                break;
            }
        }

        if (find_index != null) {
            that.timeliner.current_list = all_notes.slice(i);
        }
    }

    this.toogleCreateNote = function() {
        $(this).toggleClass('create-note-btn-not-active btn-success');
        $('.create-note-block').toggle();
    }

    this.filtered = function(page, search) {
        if (page == 3) {
            return that.filters.projects == search.project;
        } else if (page == 4) {
            return that.filters.tags == search.tag;
        } else if (page == 1) {
            return true;
        }
    }

    this.preloading = function(count) {
        that.countPreload++;
        if (that.countPreload == count) {
            that.isPreload = true;
            $('#load-screen').css({
                'display': 'block'
            });
            $('body').css({
                'overflow': 'auto'
            });
        }
    }

    this.getMetaFiles = function(search_type) {
        var req = {
            method: 'GET',
            url: this.url.getFullPath('dropbox.getMetaFiles'),
            params: {
                'search_type': search_type
            }
        };

        $http(req).success(function(data) {
            (search_type == 'projects') ?
                that.user.projects = data['result'] : that.user.tags = data['result'];
                that.preloading(3);
        });
    }

    this.getNotes = function(mode) {
        var path = (mode == 'fast') ? 'dropbox.getNotesFast' : 'dropbox.getNotesSlow';
        $http.get(this.url.getFullPath(path)).success(function(data) {
            that.user.notes.order.full_info = data['result'];
            that.user.notes.order.form_date = data['format_result'];
            that.user.notes.clear = data['order'];
            that.preloading(3);
            console.log(that.user.notes);
        });
    }


    this.addDelMeta = function(search_type, action){
        var req = {
            method: 'GET',
            url: this.url.getFullPath('dropbox.addDelNotes'),
            params: {
                'action': action,
                'search_type': search_type
            }
        }

        if (search_type === 'projects') {
            var user_choice = that.user.choices.projects;
            var user_all = that.user.projects;
        } else {
            var user_choice = that.user.choices.tags;
            var user_all = that.user.tags;
        }
        if (action == 'add') {
            if (user_choice) {
                req.params.query_name = user_choice;
                $http(req)
                    .success(function(data) {
                        user_all.push(user_choice)
                        that.refreshSettings();
                        that.messages.success.settings = data['res']
                    })
                    .error(function(data) {
                         if (search_type === 'projects') {
                            that.user.choices.errors.projects = data;
                            that.user.choices.errors.tags = '';
                            that.user.choices.tags = '';
                        } else {
                            that.user.choices.errors.tags = data;
                            that.user.choices.errors.projects = '';
                            that.user.choices.projects = '';
                        }
                        that.messages.success.settings = '';
                    });
            }
        }
    }

    this.refreshSettings = function() {
        that.user.choices.projects = '';
        that.user.choices.tags = '';
        that.user.choices.errors.projects = '';
        that.user.choices.errors.tags = '';
    }


    this.startPage = function() {
        that.getMetaFiles('tags');
        that.getMetaFiles('projects');
        that.getNotes('slow');
    }

    that.startPage();
}
