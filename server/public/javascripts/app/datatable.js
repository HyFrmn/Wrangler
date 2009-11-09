taskTableDefs = [{ 
					key: 'id',
					label: 'ID',
				},
				{
					key: 'status',
					label: 'Status',
				},
				{
					key: 'priority',
					label: 'Priority'
				},
				{
					key: 'command',
					label: 'Command'
				},
				
];

var DataTable = Class.create();

DataTable.prototype = {
	initialize: function(element, def, options){
		this.element = element;

		this.options = Object.extend({
			data: false,
			url: false,
			pageCount: 10,
			paginate: false,
			search: false,
			headerClass: 'data-table-header',
		}, options || {});
		
        this.ajaxParams = {
            page: 1,
		}
		this.parseDefs(def);
		this.container = $(element);
		this.createTable();
		this.getData(this.createRows.bind(this));
	},
	parseDefs : function(def){
		this.def = new Array();
		def.each(function(d){
			d = Object.extend({
				key: null,
				label: null,
				clickCallback: null,
				formatter: null, 
			}, d);
			this.def.push(d)
		}.bind(this))
	},
	getData : function(callback){
		if (!this.options.data && !this.options.url){alert(this.msgs.errorData);}
		this.data = this.options.data ? this.options.data : false;
		if(this.data) {callback(); } else { this.getAjaxData(this.options.url, callback); }
	},
	getAjaxData : function(url, callback){
		var transmit = new Ajax.Request(url,{
			onLoading : function(){ $(this.element).update(this.msgs.loading); }.bind(this),
			onSuccess: function(transport) {
				this.data = transport.responseJSON;
				callback();
			}.bind(this),
			onFailure : function(){ alert(this.msgs.errorURL);},
			parameters : this.ajaxParams
		});
	},
	createCache : function(){
		this.cache = this.data
	},
	createTable : function(){
		this.table = Builder.node('table', {class: 'data-table', id: (this.element + '-data-table')});
		this.container.appendChild(this.table);
		this.createHeader();
	},
	createHeader : function(){
		thead = Builder.node('thead');
		tr = Builder.node('tr', {class: this.options.headerClass});
		thead.appendChild(tr);
		this.def.each(function(d){
			td = Builder.node('td');
			td.innerHTML = d.label;
			tr.appendChild(td);
		}.bind(this));
		this.table.appendChild(thead);
	},
	createRows : function(){
		console.log(this);
		even = false;
		this.data.each(function(data){
			tr = this.createRow(data);
			if (even){
				tr.addClassName('even');
				even=false;
			} else {
				tr.addClassName('odd');
				even=true;
			}
		}.bind(this));
	},
	createRow : function(data){
		var tr = Builder.node('tr');
		var values = Object.values(data);
		
		this.def.each(function(d){
			td = Builder.node('td',{ field: d.key});
			td.innerHTML = data[d.key];
			if (d.clickCallback){
				td.observe('click', selectJobCallback)
			}
			tr.appendChild(td);
		}.bind(this));	
		this.table.appendChild(tr);
		return tr
	},
	clearRows : function(){
		even = true
		this.table.childElements().slice(1).forEach(function(child){
			this.table.removeChild(child);
		}.bind(this));
	},
	updateTable : function(url, callback){
		this.options.url = url
		this.clearRows()
		this.getData(function(){
			this.createRows();
			callback();
			}.bind(this));
	},
    nextPage : function(callback){
        this.ajaxParams.page += 1;
        this.updateTable(this.options.url, callback);
    },
    prevPage : function(callback){
        this.ajaxParams.page -= 1;
        if (this.ajaxParams.page < 1){
            this.ajaxParams.page = 1;
        }
        this.updateTable(this.options.url, callback);
    }	
	
}
