def get_file_as_string(filename)
  data = ''
  f = File.open(filename, "r") 
  f.each_line do |line|
    data += line
  end
  return data
end


class TaskLog < ActiveRecord::Base
	belongs_to :task
	
	def stdout
	  filepath = ENV['WRANGLER_HOME'] + '/logs/' + self[:task_id].to_s + '_out.log'
	  return get_file_as_string(filepath)
	end

	def stderr
	  filepath = ENV['WRANGLER_HOME'] + '/logs/' + self[:task_id].to_s + '_err.log'
	  return get_file_as_string(filepath)
	end
end
