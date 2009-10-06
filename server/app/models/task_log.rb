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
	  filepath = self[:stdout]
	  return get_file_as_string(filepath)
	end

	def stderr
	  filepath = self[:stderr]
	  return get_file_as_string(filepath)
	end
end
