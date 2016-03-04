var MainController = function($http) {

    var that = this;

    this.isPreload = false;
    this.countPreload = 0;

    this.url = {
        server: 'http://127.0.0.1:8000/',
        dropbox: {
            getMetaFiles: 'dropbox/get_meta_files/',
            getNotesFast: 'dropbox/get_notes_final/',
            getNotesSlow: 'dropbox/get_notes_alt/',
            addDelNotes: 'dropbox/add_or_del_meta_files/'
        },

        getFullPath: function(path) {
            return this.server + eval('this.' + path);
        }
    }

    this.user = {
        projects: '',
        tags: '',
        notes: {
            order: {
                full_info: '',
                form_date: ''
            },
            unorder: '',
        },
        choices: {
            projects: '',
            tags: '',
            errors: {
                projects: '',
                tags: ''
            }
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
            that.preloading(3);
            that.user.notes.order.form_date = data['format_result'];
            console.log(that.user.notes.order);
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
        that.getNotes('fast');
    }

    that.startPage();
}
