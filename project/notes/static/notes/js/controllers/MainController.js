var MainController = function($http, $scope) {

    var that = this;

    this.isPreload = false;
    this.isLoadFiles = false;
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
            downloadFile: 'dropbox/download_file/',
            delNote: 'dropbox/delete_note/'
        },
        auth: {
            logout: 'auth/logout/'
        },

        getStaticPath: function(path, file_name) {
            console.log(this.server + 'static/' + path + file_name);
            return '/static/' + path + file_name;
        },

        getFullPath: function(path) {
            return this.server + eval('this.' + path);
        },

        getFileDownloadPath: function(file_name) {
            return this.server + this.dropbox.downloadFile + '?path=' + file_name;
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
        },
        edit: {
            text: '',
        }
    }

    this.messages = {
        success: {
            settings: '',
            notes: {
                create: ''
            }
        },
        errors: {
            preloading: false
        }
    }

    this.filters = {
        projects: 'notebook',
        tags: 'tag',
        searchSystem: []
    }

    this.timeliner = {
        date: '',
        current_list: [],

        groupDate: function(y, m, d) {
            return y + ' ' + m + ' ' + d;
        }
    }

    this.clearSuccessMessage = function() {
        that.messages.success.settings = '';
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
            // that.user.notes.order.form_date
            var form_date = that.user.notes.order.form_date;

            date_list = data['obj']['date'].split('/');
            var year = date_list[1],
                month = date_list[2].toLowerCase(),
                day = date_list[3];

            if (form_date.hasOwnProperty(year)) {
                if (form_date[year].hasOwnProperty(month)) {
                    if (form_date[year][month].hasOwnProperty(day)) {
                        form_date[year][month][day].push(data['obj'].path);
                    } else {
                        form_date[year][month][day] = [data['obj'].path];
                    }
                } else {
                    form_date[year][month] = {};
                    form_date[year][month][day] = [data['obj'].path];
                }
            } else {
                form_date[year] = {};
                form_date[year][month] = {};
                form_date[year][month][day] = [data['obj'].path];
            }
            that.timeliner.current_list.push(data['obj']);
            that.messages.success.notes.create = 'Note successfully created'

            // var loc_req = {
            //     method: 'POST',
            //     url: that.url.getFullPath('dropbox.format_to_date'),
            //     data: {
            //         new_note: data['obj'],
            //         notes: that.user.notes.order.form_date
            //     }
            // };
            // $http(loc_req).success(function(data) {
            //     // that.user.notes.order.form_date = data['notes'];
            // });
        });
    }

    this.editNote = function(index, note_path) {
        that.isLoadFiles = true;
        var new_text = $('#note-edit-text-' + index).val();
        var req = {
            method: 'POST',
            url: that.url.getFullPath('dropbox.createEditNote'),
            data: {
                'text': new_text,
                'action': 'edit',
                'path': note_path
            }
        };

        $http(req).success(function() {
            that.isLoadFiles = false;
            var all_notes = that.user.notes.order.full_info;
            for (var i = 0; i < all_notes.length; i++) {
                if (all_notes[i].path == note_path) {
                    all_notes[i].text = new_text;
                    break;
                }
            }
        }).error(function() {
            that.isLoadFiles = false;
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
        that.isLoadFiles = true;
        var path = this.note.path;
        var fd = new FormData();
        fd.append("file", $("input[data-file='file_" + path + "']")[0].files[0]);
        fd.append("path", path);

        url = that.url.getFullPath('dropbox.uploadFile');

        $http.post(url, fd, {
            headers: {'Content-Type': undefined },
            transformRequest: angular.identity
        })
            .success(function(data) {
                var notes = that.user.notes.order.full_info
                for (var i = 0; i < notes.length; i++) {
                    if (notes[i].path == path) {
                        if (notes[i].files) {
                            notes[i].files.push(data['res']);
                        } else {
                            notes[i].files = [data['res']];
                        }
                    }
                }
                that.isLoadFiles = false;
            })
            .error(function() {
                that.isLoadFiles = false;
            });
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
        console.log(all_notes);
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

            $('#load-screen').css({'display': 'block'});
            $('body').css({'overflow': 'auto'});

            $('[data-toggle="tooltip"]').tooltip();

            that.prepairSearchSystem();

            $('#search-field').autocomplete({source: that.filters.searchSystem});
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
        }).error(function(data) {
            that.messages.errors.preloading = true;
        });
    }

    this.delNote = function(path) {
        that.isLoadFiles = true;

        var req = {
            method: 'POST',
            url: this.url.getFullPath('dropbox.delNote'),
            data: {
                'path': path
            }
        };

        $http(req)
            .success(function() {
                // Remove element from clear array
                var all_notes_clear = that.user.notes.clear;
                for (var i = 0; i < all_notes_clear.length; i++) {
                    if (all_notes_clear[i] == path) {
                        all_notes_clear.splice(i, 1);
                    }
                }

                // Remove element from full info array
                var all_notes_full_info = that.user.notes.order.full_info;
                for (var i = 0; i < all_notes_full_info.length; i++) {
                    if (all_notes_full_info[i].path == path) {
                        all_notes_full_info.splice(i, 1);
                    }
                }

                // Remove element from form date array
                var all_notes_form_date = that.user.notes.order.form_date;
                list_path = path.split('/');
                var year = list_path[1],
                    month = list_path[2].toLowerCase(),
                    day = list_path[3];

                // var all_notes_form_date = that.user.notes.order.form_date[year][month][day];

                // for (var i = 0; i < all_notes_form_date.length; i++) {
                //     if (all_notes_form_date[i] == path) {
                //         var index = i;
                //     }
                // }

                if (all_notes_form_date[year][month][day].length == 1) {
                    if (all_notes_form_date[year][month].length == 1) {
                        if (all_notes_form_date[year].length == 1) {
                            delete all_notes_form_date[year];
                        } else {
                            delete all_notes_form_date[year][month];
                        }
                    } else {
                        delete all_notes_form_date[year][month][day];
                    }
                } else {
                    var index = all_notes_form_date[year][month][day].indexOf(path);
                    all_notes_form_date[year][month][day].splice(index, 1);
                }

                // Remove element from current list
                var all_notes_current_list = that.timeliner.current_list;
                for (var i = 0; i < all_notes_current_list.length; i++) {
                    if (all_notes_current_list[i].path == path) {
                        all_notes_current_list.splice(i, 1);
                    }
                }
                that.isLoadFiles = false;
            })
        .error(function() {
            that.isLoadFiles = false;
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

    this.prepairSearchSystem = function() {
        var all_notes = that.user.notes.order.full_info;
        for (var i in all_notes) {
            var text = all_notes[i].text;
            if (text.length > 40) {
                text = text.slice(0, 37) + '...'
            }
            that.filters.searchSystem.push(text);
        }
    }

    // this.showInfo = function() {
    //     console.log(that.user.notes);
    //     console.log('-------');
    //     console.log(that.timeliner);
    // }

    this.startPage = function() {
        that.getMetaFiles('tags');
        that.getMetaFiles('projects');
        that.getNotes('slow');
    }

    // this.loadFile = function() {
    //     $('#smoky').toggleClass('smoke');
    // }

    that.startPage();
}
