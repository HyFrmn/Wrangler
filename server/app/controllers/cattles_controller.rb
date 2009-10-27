class CattlesController < ApplicationController
  # GET /cattles
  # GET /cattles.xml
  def index
    @cattles = Cattle.all

    respond_to do |format|
      format.html # index.html.erb
      format.xml  { render :xml => @cattles }
      format.json { render :json => @cattles }
    end
  end

  # GET /cattles/1
  # GET /cattles/1.xml
  def show
    @cattle = Cattle.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.xml  { render :xml => @cattle }
    end
  end

  # GET /cattles/new
  # GET /cattles/new.xml
  def new
    @cattle = Cattle.new

    respond_to do |format|
      format.html # new.html.erb
      format.xml  { render :xml => @cattle }
    end
  end

  # GET /cattles/1/edit
  def edit
    @cattle = Cattle.find(params[:id])
  end

  # POST /cattles
  # POST /cattles.xml
  def create
    @cattle = Cattle.new(params[:cattle])

    respond_to do |format|
      if @cattle.save
        flash[:notice] = 'Cattle was successfully created.'
        format.html { redirect_to(@cattle) }
        format.xml  { render :xml => @cattle, :status => :created, :location => @cattle }
      else
        format.html { render :action => "new" }
        format.xml  { render :xml => @cattle.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /cattles/1
  # PUT /cattles/1.xml
  def update
    @cattle = Cattle.find(params[:id])

    respond_to do |format|
      if @cattle.update_attributes(params[:cattle])
        flash[:notice] = 'Cattle was successfully updated.'
        format.html { redirect_to(@cattle) }
        format.xml  { head :ok }
      else
        format.html { render :action => "edit" }
        format.xml  { render :xml => @cattle.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /cattles/1
  # DELETE /cattles/1.xml
  def destroy
    @cattle = Cattle.find(params[:id])
    @cattle.destroy

    respond_to do |format|
      format.html { redirect_to(cattles_url) }
      format.xml  { head :ok }
    end
  end
  
  def list
    @cattles = Cattle.all
    
    render :partial => 'list'
  end
end
