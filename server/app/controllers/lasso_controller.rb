require 'xmlrpc/client'

class LassoController < ApplicationController
  def sleep
    server = XMLRPC::Client.new(params[:hostname], "/RPC2", 6789)
    result = server.call("sleep")
    render :json => result
  end
  
  def wake
    server = XMLRPC::Client.new(params[:hostname], "/RPC2", 6789)
    result = server.call("wake_up")
    render :json => result
  end
  
end
