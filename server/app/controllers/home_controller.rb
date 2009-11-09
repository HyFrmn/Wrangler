class HomeController < ApplicationController
  def index
    @jobs = Job.find(:all, :order => "id desc")
    respond_to do |format|
      format.html # index.html.erb
      format.xml  { render :xml => @jobs }
      format.json { render :json => @jobs.to_json(:except => :meta, :methods => [:progress, :finished, :running, :queued, :waiting, :estimate, :runtime, :priority] ) }
    end
  end 
end
