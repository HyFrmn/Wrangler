require 'xmlrpc/client'

class JobsController < ApplicationController
  # GET /jobs
  # GET /jobs.xml
  # GET /jobs.json
  def index
    @jobs = Job.find(:all, :order => "id desc")
    respond_to do |format|
      format.html # index.html.erb
      format.xml  { render :xml => @jobs }
      format.json { render :json => @jobs.to_json(:except => :meta, :methods => [:progress, :finished, :running, :queued, :waiting, :estimate, :runtime, :priority] ) }
    end
  end

  # GET /jobs/1
  # GET /jobs/1.xml
  def show
    @job = Job.find(params[:id])
    @tasks = @job.tasks
    respond_to do |format|
      format.html # show.html.erb
      format.xml  { render :xml => @job }
    end
  end

  # GET /jobs/new
  # GET /jobs/new.xml
  def new
    @job = Job.new

    respond_to do |format|
      format.html # new.html.erb
      format.xml  { render :xml => @job }
    end
  end

  # GET /jobs/1/edit
  def edit
    @job = Job.find(params[:id])
  end

  # POST /jobs
  # POST /jobs.xml
  def create
    @job = Job.new(params[:job])

    respond_to do |format|
      if @job.save
        flash[:notice] = 'Job was successfully created.'
        format.html { redirect_to(@job) }
        format.xml  { render :xml => @job, :status => :created, :location => @job }
      else
        format.html { render :action => "new" }
        format.xml  { render :xml => @job.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /jobs/1
  # PUT /jobs/1.xml
  def update
    @job = Job.find(params[:id])

    respond_to do |format|
      if @job.update_attributes(params[:job])
        flash[:notice] = 'Job was successfully updated.'
        format.html { redirect_to(@job) }
        format.xml  { head :ok }
      else
        format.html { render :action => "edit" }
        format.xml  { render :xml => @job.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /jobs/1
  # DELETE /jobs/1.xml
  def destroy
    @job = Job.find(params[:id])
    @job.destroy

    respond_to do |format|
      format.html { redirect_to(jobs_url) }
      format.xml  { head :ok }
    end
  end
  
  def list
    items_per_page = 10
    page = params[:page] ? params[:page].to_i : 1
    
    conditions = "" unless params[:filter].nil?
    
    @total = Job.count(:conditions => conditions)
    @jobs = Job.find(:all, :order => "id desc", :conditions => conditions,  :offset => ((page - 1) * items_per_page), :limit => items_per_page)
    respond_to do |format|
        format.html { render :partial => 'list' }
        format.xml { render :xml => @jobs.to_xml(:except => :meta, :methods => [:progress, :finished, :running, :queued, :waiting, :estimate, :runtime, :priority] )  }
        format.json { render :json => @jobs.to_json(:except => :meta, :methods => [:progress, :finished, :running, :queued, :waiting, :estimate, :runtime, :priority] )  }
    end
  end
  
  
  #AJAX Handlers 
  
  def rename
    id = params[:job_id].to_i
    name = params[:job_name]
    server = XMLRPC::Client.new(AppConfig.lasso_host, "/RPC2", AppConfig.lasso_port)
    result = server.call("job_rename", id, name)
    render :text => result
  end
  
  def priority
    puts params
    id = params[:job_id].to_i
    priority = params[:job_priority]
    server = XMLRPC::Client.new(AppConfig.lasso_host, "/RPC2", AppConfig.lasso_port)
    result = server.call("job_priority", id, priority)
    render :text => result
  end
  
  def queue
    id = params[:job_id].to_i
    if id = 0 
      id = params[:id].to_i
    end
    server = XMLRPC::Client.new(AppConfig.lasso_host, "/RPC2", AppConfig.lasso_port)
    result = server.call("job_queue", id)
    render :text => result
  end

  def pause
    id = params[:job_id].to_i
    if id = 0 
      id = params[:id]
    end
    server = XMLRPC::Client.new(AppConfig.lasso_host, "/RPC2", AppConfig.lasso_port)
    result = server.call("job_pause", id)
    render :text => result
  end
  
  def stop
    id = params[:job_id].to_i
    if id = 0 
      id = params[:id]
    end
    server = XMLRPC::Client.new(AppConfig.lasso_host, "/RPC2", AppConfig.lasso_port)
    result = server.call("job_stop", id)
    render :text => result
  end
end
